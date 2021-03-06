from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # engine = create_engine('postgresql://postgres:filak@localhost:5432/postgres', convert_unicode=True)
engine = create_engine('mysql+mysqldb://fbkviz:VikenfoveLeharo@fbkviz.mysql.pythonanywhere-services.com/fbkviz$fbkviz?charset=utf8', pool_recycle=280, encoding='utf-8')
session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)
