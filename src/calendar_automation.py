from dataclasses import dataclass
from abc import ABC, abstractmethod
from main import RefeicaoRegistro, TipoRefeicao
import sqlalchemy as sa
from sqlalchemy.orm import Session
import datetime
import enum



class DaysOfWeek(enum.Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5


class AbstractCalendar(ABC):
    """Abstract class for calendar integration.
    Subclasses should implement the methods to add events to a specific calendar service.
    
    Attributes:
        start_times (dict): A dictionary mapping start meal events to days of the week 
        (lunch/dinner).
        event_length (datetime.timedelta): The length of each event.
    
    Methods:
        __init__(API_KEY: str, color: str): Initializes the calendar with API key and optional color.
        add_event(event: CalendarEvent): Adds an event to the calendar.
    """
    start_times: dict[DaysOfWeek, tuple[datetime.time|None, datetime.time | None]] = {
        DaysOfWeek.MONDAY: (datetime.time(11, 0), datetime.time(17, 15)),
        DaysOfWeek.TUESDAY: (datetime.time(11, 30), datetime.time(17, 15)),
        DaysOfWeek.WEDNESDAY: (datetime.time(11, 0), datetime.time(17, 15)),
        DaysOfWeek.THURSDAY: (datetime.time(12, 0), datetime.time(17, 15)),
        DaysOfWeek.FRIDAY: (datetime.time(11, 0), datetime.time(17, 15)),
        DaysOfWeek.SATURDAY: (datetime.time(11, 0), None)}
    event_length: datetime.timedelta = datetime.timedelta(hours=1)

    @abstractmethod
    def __init__(self, API_KEY: str, color: str = "red"):
        pass

    @abstractmethod
    def add_event(self, event: RefeicaoRegistro)->None:
        pass

class GoogleCalendar(AbstractCalendar):
    """Google Calendar integration class.
    This class implements the methods to add events to a Google Calendar.
    
    Attributes:
        API_KEY (str): The API key for Google Calendar.
        color (str): The color of the calendar events.
    """
    
    def __init__(self, API_KEY: str, color: str = "red"):
        self.API_KEY = API_KEY
        self.color = color

    def add_event(self, event: RefeicaoRegistro) -> None:
        pass

if __name__ == "__main__":
    db_engine = sa.create_engine("sqlite:///../bandeijao_usp_sao_carlos.db") 
    with Session(db_engine) as session:
        filter_data = datetime.date.today()
        refeicoes = session.query(RefeicaoRegistro).filter(
            RefeicaoRegistro.data_refeicao >= filter_data).all()
        calendar=GoogleCalendar("iaehgea")
        for refeicao in refeicoes:
            calendar.add_event(refeicao)
            print(refeicao)