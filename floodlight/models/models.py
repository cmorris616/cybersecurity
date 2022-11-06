from cgi import print_form
from email.headerregistry import ParameterizedMIMEHeader
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, CLOB, DateTime
from sqlalchemy.orm import relationship

Base = declarative_base()


def create_tables(engine):
    Base.metadata.create_all(engine)


class Host(Base):
    __tablename__ = 'hosts'

    id = Column('id', Integer, primary_key=True)
    host_name = Column('host_name', String(255))
    parent_id = Column('parent_id', Integer)
    nmap_results = relationship('NmapResult', backref='hosts')
    last_seen = Column('last_seen', DateTime)


class NmapResult(Base):
    __tablename__ = 'nmap_results'

    id = Column('id', Integer, primary_key=True)
    host_id = Column('host_id', Integer, ForeignKey('hosts.id'))
    port = Column('port', Integer)
    protocol = Column('protocol', String(50))
    service = Column('service', String(255))
    state = Column('state', String(50))
    details = Column('details', CLOB)
    last_seen = Column('last_seen', DateTime)


class Log4jScanResult(Base):
    __tablename__ = 'log4j_scan_results'

    id = Column('id', Integer, primary_key=True)
    host_id = Column('host_id', Integer, ForeignKey('hosts.id'))
    command = Column('command', CLOB)
    output = Column('output', CLOB)
    scan_date_time = Column('scan_date_time', DateTime)
