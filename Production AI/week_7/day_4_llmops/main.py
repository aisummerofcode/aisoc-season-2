"""
Multi-Platform Post Rewriter using Google Cloud Functions + Vertex AI
====================================================================

This Cloud Function:
1. Accepts CSV uploads with 'source' and 'post' columns
2. Uses Vertex AI Gemini to rewrite each post in a professional brand tone
3. Returns an Excel file (.xlsx) with the rewritten posts

Input CSV format:
- id (optional): unique identifier
- source: platform name (linkedin, twitter, instagram, slack, email, etc.)
- post: original text content to rewrite

Output Excel format:
- id: preserved from input or auto-generated
- source: platform name
- rewritten_post: AI-generated branded version

Author: Your Name
Date: 2025-09-27
"""

import io
import pandas as pd
import vertexai
from vertexai.generative_models import GenerativeModel
from flask import Request

def process_csv(request: Request):
    """
    Main Cloud Function entry point.
    
    Args:
        request (flask.Request): HTTP request object containing uploaded CSV file
        
    Returns:
        tuple: (Excel file bytes, HTTP status code, headers)
    """
    
    # Initialize Vertex AI client
    # Replace 'doc-rewriter-project' with your actual project ID
    vertexai.init(project="doc-rewriter-project", location="us-central1")
    model = GenerativeModel("gemini-2.5-flash")  # Current stable Gemini model
    
    # Validate file upload
    if "file" not in request.files:
        return {"error": "Upload a CSV file with field name 'file'."}, 400
    
    # Read uploaded CSV into pandas DataFrame
    try:
        df = pd.read_csv(request.files["file"])
    except Exception as e:
        return {"error": f"Failed to read CSV: {str(e)}"}, 400
    
    # Validate required columns exist
    if not {"source", "post"}.issubset(df.columns):
        return {"error": "CSV must contain 'source' and 'post' columns"}, 400
    
    # Process each row and generate rewrites
    rewrites = []
    for index, row in df.iterrows():
        text = str(row["post"])
        source = str(row["source"])
        
        try:
            # Create prompt for brand-consistent rewriting
            prompt = (
                f"Rewrite this {source} post in a professional, engaging, and "
                f"brand-consistent tone. Keep it concise, impactful, and appropriate "
                f"for the platform. Maintain any emojis if they fit the brand voice:\n\n{text}"
            )
            
            # Call Vertex AI Gemini model
            response = model.generate_content(prompt)
            rewrites.append(response.text.strip())
            
        except Exception as e:
            # Handle individual row errors gracefully
            rewrites.append(f"Error processing row {index + 1}: {str(e)}")
    
    # Build output DataFrame
    output_df = pd.DataFrame({
        "id": df.get("id", range(1, len(df) + 1)),  # Use existing ID or auto-generate
        "source": df["source"],
        "rewritten_post": rewrites
    })
    
    # Create Excel file in memory
    output_buffer = io.BytesIO()
    try:
        output_df.to_excel(
            output_buffer, 
            index=False, 
            sheet_name="RewrittenPosts",
            engine='openpyxl'
        )
        output_buffer.seek(0)
    except Exception as e:
        return {"error": f"Failed to create Excel file: {str(e)}"}, 500
    
    # Return Excel file with proper headers
    return (
        output_buffer.getvalue(),
        200,
        {
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "Content-Disposition": "attachment; filename=rewritten_posts.xlsx"
        },
    )
