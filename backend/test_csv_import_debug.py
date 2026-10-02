import asyncio
import os
from app.core.database import AsyncSessionLocal
from app.services.lead_service import LeadService

async def test_import():
    files = [
        "01_clinica_estetica_completo.csv",
        "02_odontologia_alta_complexidade.csv",
        "03_vendas_b2b_software.csv",
        "04_metas_e_indicadores_mensal.csv"
    ]
    
    async with AsyncSessionLocal() as session:
        service = LeadService(session, organization_id=1)
        
        for f in files:
            path = os.path.join("mockups_csv", f)
            if not os.path.exists(path):
                path = os.path.join("..", "mockups_csv", f)
            
            with open(path, "rb") as fp:
                content = fp.read()
            
            print(f"\n--- Testing import of {f} ---")
            try:
                res = await service.import_csv(content)
                print(f"Success! Total: {res.total_rows}, Imported: {res.imported_count}, Failed: {res.failed_count}")
                if res.errors:
                    print("Errors:", res.errors)
            except Exception as e:
                print(f"EXCEPTION ON {f}: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_import())
