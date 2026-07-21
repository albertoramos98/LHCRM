from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class CRMProvider(ABC):
    """
    Generic CRM Provider Interface.
    Allows seamlessly plugging in Kommo, Hubspot, Pipedrive, RDStation, Salesforce, etc.
    """
    
    @abstractmethod
    async def get_users(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_contacts(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_companies(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_pipelines(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_leads(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_tasks(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_events(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_custom_fields(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_tags(self) -> List[Dict[str, Any]]:
        pass
