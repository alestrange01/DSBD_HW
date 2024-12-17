from models.ticker_management import TickerManagement
from dto.ticker_management import TickerManagementDTO

class TickerManagementRepositoryReader:
    def __init__(self, session):
        self.session = session
        
    def get_all_ticker_management(self):
        with self.session as session:
            ticker_managements = session.query(TickerManagement).all()
            ticker_managements_dto = []
            for ticker_management in ticker_managements:
                ticker_management_dto = TickerManagementDTO(share_cod=ticker_management.share_cod, counter=ticker_management.counter)
                ticker_managements_dto.append(ticker_management_dto)
            return ticker_managements_dto
    