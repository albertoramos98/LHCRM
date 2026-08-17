import json
import os
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)

async def generate_dashboard_html(
    session: AsyncSession,
    organization_id: int = 1,
    output_path: str = "static/dashboard.html"
) -> str:
    """
    Compiles dashboard metrics for a specific organization, renders them into
    the HTML template, and writes the resulting standalone file.
    """
    try:
        # 1. Fetch metrics from the DashboardService scoped to tenant
        dashboard_service = DashboardService(session, organization_id=organization_id)
        metrics = await dashboard_service.get_all_metrics(period="30days")
        
        # 2. Setup paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(base_dir, "templates", "public_dashboard.html")
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file not found at: {template_path}")
            
        # 3. Read base template
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()
            
        # 4. Serialize data and create timestamp
        serialized_data = json.dumps(metrics, default=str)
        last_updated_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # 5. Replace placeholders in the HTML
        rendered_content = template_content.replace("{{DASHBOARD_DATA_JSON}}", serialized_data)
        rendered_content = rendered_content.replace("{{LAST_UPDATED}}", last_updated_str)
        
        # 6. Ensure target directory exists and save
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_content)
            
        logger.info(f"HTML dashboard for Org {organization_id} successfully written to: {output_path}")
        return rendered_content

    except Exception as e:
        logger.error(f"Failed to generate HTML dashboard for Org {organization_id}: {e}", exc_info=True)
        raise e
