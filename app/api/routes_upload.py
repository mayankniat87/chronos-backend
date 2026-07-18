import io
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, date

import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.menu_ai.context_builder import invalidate_menu_context
from app.models.restaurant import (
    Restaurant, MenuItem, Supplier, InventoryItem,
    Staff, Customer, Order, OrderItem, Expense, DecisionLog
)

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["Upload"])

# Topological order of models based on dependency tree
MODEL_ORDER = [
    ("restaurants", Restaurant),
    ("suppliers", Supplier),
    ("menu_items", MenuItem),
    ("inventory_items", InventoryItem),
    ("staff", Staff),
    ("customers", Customer),
    ("orders", Order),
    ("order_items", OrderItem),
    ("expenses", Expense),
    ("decisions_log", DecisionLog),
]

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize DataFrame column names: lowercase, replace spaces/dashes with underscores.
    Replaces NaN values with None.
    """
    df = df.copy()
    # Normalize headers
    df.columns = [
        str(c).strip().lower().replace(" ", "_").replace("-", "_") 
        for c in df.columns
    ]
    # Replace NaN/NaT with None for database compatibility
    df = df.where(pd.notnull(df), None)
    return df

def parse_date(val: Any) -> Optional[date]:
    """Parse various date formats safely."""
    if val is None:
        return None
    if isinstance(val, (date, datetime)):
        return val.date() if isinstance(val, datetime) else val
    try:
        return pd.to_datetime(val).date()
    except Exception:
        logger.warning(f"Failed to parse date: {val}")
        return None

def parse_datetime(val: Any) -> Optional[datetime]:
    """Parse various datetime formats safely."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    if isinstance(val, date):
        return datetime.combine(val, datetime.min.time())
    try:
        return pd.to_datetime(val).to_pydatetime()
    except Exception:
        logger.warning(f"Failed to parse datetime: {val}")
        return None

def parse_json(val: Any) -> Any:
    """Parse string representations of JSON safely, or return object as-is."""
    if val is None:
        return None
    if isinstance(val, (dict, list)):
        return val
    if isinstance(val, str):
        try:
            return json.loads(val)
        except json.JSONDecodeError:
            # If it's a plain string, return it wrapped or as is
            return val
    return val

def import_table_data(
    model_name: str, 
    model_cls: Any, 
    df: pd.DataFrame, 
    db: Session, 
    clear_existing: bool,
    restaurant_id_override: Optional[int] = None
) -> int:
    """
    Validates, parses, and persists a DataFrame into a specific SQLAlchemy model table.
    """
    df = clean_df(df)
    
    # 1. Clear existing records for this model if requested
    # For a hackathon demo, clearing the database/table for the uploaded restaurant ensures a clean slate
    if clear_existing:
        if model_cls == Restaurant:
            # If we clear restaurants, Cascade delete takes care of child tables
            # Find unique restaurant IDs in the upload to selectively clear
            if "id" in df.columns:
                r_ids = df["id"].dropna().unique().tolist()
                for r_id in r_ids:
                    db.query(Restaurant).filter(Restaurant.id == int(r_id)).delete()
        else:
            # Clear based on restaurant_id column if present
            if "restaurant_id" in df.columns:
                r_ids = df["restaurant_id"].dropna().unique().tolist()
                if restaurant_id_override:
                    r_ids.append(restaurant_id_override)
                r_ids = list(set(r_ids))
                for r_id in r_ids:
                    db.query(model_cls).filter(model_cls.restaurant_id == int(r_id)).delete()
            elif restaurant_id_override and hasattr(model_cls, "restaurant_id"):
                db.query(model_cls).filter(model_cls.restaurant_id == restaurant_id_override).delete()

    # 2. Iterate and insert
    count = 0
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        
        # Strip out columns that don't match model properties
        model_fields = {c.name for c in model_cls.__table__.columns}
        insert_data = {}
        
        for field, val in row_dict.items():
            if field in model_fields:
                insert_data[field] = val
        
        # Override restaurant_id if provided
        if restaurant_id_override and "restaurant_id" in model_fields:
            insert_data["restaurant_id"] = restaurant_id_override

        # Field-specific typing and formatting
        # Date fields
        if "date" in insert_data:
            insert_data["date"] = parse_date(insert_data["date"])
        # DateTime fields
        if "decided_at" in insert_data:
            insert_data["decided_at"] = parse_datetime(insert_data["decided_at"])
        if "created_at" in insert_data:
            insert_data["created_at"] = parse_datetime(insert_data["created_at"])
        # JSON fields
        if "inputs_json" in insert_data:
            insert_data["inputs_json"] = parse_json(insert_data["inputs_json"])
        if "outcome_json" in insert_data:
            insert_data["outcome_json"] = parse_json(insert_data["outcome_json"])
        if "scenarios_json" in insert_data:
            insert_data["scenarios_json"] = parse_json(insert_data["scenarios_json"])

        # Convert churn_flag to boolean if exists
        if "churn_flag" in insert_data and insert_data["churn_flag"] is not None:
            if isinstance(insert_data["churn_flag"], str):
                insert_data["churn_flag"] = insert_data["churn_flag"].lower() in ("true", "1", "yes")
            else:
                insert_data["churn_flag"] = bool(insert_data["churn_flag"])

        # Instantiate model and add to DB
        # If there is a primary key 'id' in row and it's not None, keep it (allows explicit seeding)
        # SQLAlchemy handles explicit IDs correctly if autoincrement sequence is aligned.
        db_item = model_cls(**insert_data)
        db.add(db_item)
        count += 1
        
    db.commit()
    logger.info(f"Successfully imported {count} records into {model_name}.")
    return count

@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    clear_existing: bool = Query(True, description="Delete existing records of the restaurant being imported to avoid duplicates"),
    restaurant_id: Optional[int] = Query(None, description="Manually override or specify target restaurant ID (highly recommended for single CSV uploads)"),
    db: Session = Depends(get_db)
):
    """
    Accepts an Excel workbook (.xlsx) with multiple sheets representing database tables, 
    or a single CSV file representing a specific table.
    
    Expected Excel sheet names (or CSV file names):
    - restaurants
    - suppliers
    - menu_items
    - inventory_items
    - staff
    - customers
    - orders
    - order_items
    - expenses
    - decisions_log
    """
    filename = file.filename.lower()
    file_bytes = await file.read()
    
    summary: Dict[str, int] = {}
    
    # 1. Excel Parsing (.xlsx, .xls)
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        try:
            excel_file = pd.ExcelFile(io.BytesIO(file_bytes))
            sheet_names = [s.lower() for s in excel_file.sheet_names]
            
            # Map Excel sheets to DB tables. Supports plural/singular variations.
            sheet_mappings = {}
            for sheet in excel_file.sheet_names:
                normalized = sheet.strip().lower().replace(" ", "_")
                sheet_mappings[normalized] = sheet
            
            # Import sheets in topological dependency order
            for key, model_cls in MODEL_ORDER:
                # Find matching sheet
                matched_sheet = None
                # Exact plural check (e.g. "menu_items")
                if key in sheet_mappings:
                    matched_sheet = sheet_mappings[key]
                # Singular check (e.g. "menu_item")
                elif key.rstrip("s") in sheet_mappings:
                    matched_sheet = sheet_mappings[key.rstrip("s")]
                # Core stem check (e.g. "menu")
                elif key.replace("_items", "") in sheet_mappings:
                    matched_sheet = sheet_mappings[key.replace("_items", "")]
                elif key.replace("_log", "") in sheet_mappings:
                    matched_sheet = sheet_mappings[key.replace("_log", "")]
                
                if matched_sheet:
                    logger.info(f"Parsing sheet: {matched_sheet} for model {key}")
                    df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=matched_sheet)
                    if not df.empty:
                        rows_inserted = import_table_data(
                            model_name=key,
                            model_cls=model_cls,
                            df=df,
                            db=db,
                            clear_existing=clear_existing,
                            restaurant_id_override=restaurant_id
                        )
                        summary[key] = rows_inserted
                    else:
                        summary[key] = 0
            
            invalidate_menu_context(restaurant_id)
            return {
                "status": "success",
                "message": "Excel workbook processed successfully",
                "summary": summary
            }
            
        except Exception as e:
            db.rollback()
            logger.exception("Error processing Excel file")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error parsing Excel file: {str(e)}"
            )
            
    # 2. CSV Parsing (.csv)
    elif filename.endswith(".csv"):
        # For CSV files, we need to know which table they map to.
        # Check if the user specified a table name via query parameter.
        # If not, try to infer from the filename.
        target_table = None
        
        # Check query parameter
        # Try to infer from filename if not provided
        inferred_table = filename.replace(".csv", "").strip()
        
        matched_model = None
        for key, model_cls in MODEL_ORDER:
            # Check exact match or plural/singular patterns
            if inferred_table == key or inferred_table == key.rstrip("s") or inferred_table in key:
                target_table = key
                matched_model = (key, model_cls)
                break
                
        if not matched_model:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Could not infer table type from CSV name '{filename}'. "
                    f"Please name the file to match one of our models, e.g., 'menu_items.csv', 'suppliers.csv', 'orders.csv'."
                )
            )
            
        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
            if df.empty:
                return {
                    "status": "success",
                    "message": "CSV file was empty, no rows imported.",
                    "summary": {target_table: 0}
                }
                
            # If uploading a dependent table (e.g. Menu Items) via CSV without a restaurant_id in CSV,
            # and restaurant_id query param is missing, throw an error.
            df_cleaned_temp = clean_df(df)
            if (
                "restaurant_id" not in df_cleaned_temp.columns 
                and not restaurant_id 
                and matched_model[1] != Restaurant
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Please provide a 'restaurant_id' query parameter or ensure the CSV contains a 'restaurant_id' column."
                )

            rows_inserted = import_table_data(
                model_name=matched_model[0],
                model_cls=matched_model[1],
                df=df,
                db=db,
                clear_existing=clear_existing,
                restaurant_id_override=restaurant_id
            )
            
            invalidate_menu_context(restaurant_id)
            return {
                "status": "success",
                "message": f"CSV file for table '{matched_model[0]}' processed successfully",
                "summary": {matched_model[0]: rows_inserted}
            }
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error processing CSV file: {filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error parsing CSV: {str(e)}"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file format. Please upload a standard Excel (.xlsx) file or a CSV (.csv) file."
        )
