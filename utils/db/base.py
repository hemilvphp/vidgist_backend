from sqlalchemy import Column, String
from sqlalchemy.orm import as_declarative, declared_attr

@as_declarative()
class Base:
    __name__: str
    
    id = Column(String, primary_key=True, unique=True, nullable=False, index=True)
    
    @declared_attr
    def __tablename__(cls) -> str:
        old_name = cls.__name__
        prev_cap = False
        new_name = ""
        
        for index, latter in enumerate(old_name[:-1]):
            if (not prev_cap and latter.isupper()) or (
                prev_cap and latter.isupper() and 
                old_name[index + 1].islower()
            ):
                new_name += "_" + latter.lower()
                prev_cap = True
                
            else:
                new_name += latter.lower()
                prev_cap = latter.isupper()
        
        tail = old_name[-1] if old_name[-1].islower() else "_" + old_name[-1].lower()
        return (new_name + tail).lstrip("_")