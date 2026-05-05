from pathlib import Path
import numpy as np
import face_recognition
from sqlalchemy import create_engine, Column, String, Date, Boolean, ForeignKey, LargeBinary
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class CommonPerson(Base):
    __tablename__ = 'common_person'
    cpf = Column(String(11), primary_key=True)
    full_name = Column(String(255))
    mother_full_name = Column(String(255))
    birth_date = Column(Date)
    is_wanted = Column(Boolean, default=False)
    is_employee = Column(Boolean, default=False)
    encoding = Column(LargeBinary)
    
    wanted_info = relationship("Wanted", back_populates="person", uselist=False)
    employee_info = relationship("Employee", back_populates="person", uselist=False)

class Wanted(Base):
    __tablename__ = 'wanted'
    cpf = Column(String(11), ForeignKey('common_person.cpf'), primary_key=True)
    crime = Column(String(255))
    risk_level = Column(String(50))
    
    person = relationship("CommonPerson", back_populates="wanted_info")

class Employee(Base):
    __tablename__ = 'employee'
    cpf = Column(String(11), ForeignKey('common_person.cpf'), primary_key=True)
    
    person = relationship("CommonPerson", back_populates="employee_info")

base_dir = Path(__file__).resolve().parent
db_dir = base_dir / 'project_database'
db_dir.mkdir(parents=True, exist_ok=True)
db_path = db_dir / 'persons.db'

engine = create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verify_face(face_encoding_list):
    db = session_factory()
    persons = db.query(CommonPerson).all()
    
    known_encodings = []
    known_cpfs = []
    
    for person_record in persons:
        if person_record.encoding:
            known_encodings.append(np.frombuffer(person_record.encoding, dtype=np.float64))
            known_cpfs.append(person_record.cpf)
            
    if not known_encodings:
        db.close()
        return {"status": "unknown"}
        
    target_encoding = np.array(face_encoding_list)
    matches = face_recognition.compare_faces(known_encodings, target_encoding, tolerance=0.6)
    face_distances = face_recognition.face_distance(known_encodings, target_encoding)
    
    best_match_index = np.argmin(face_distances)
    
    if matches[best_match_index]:
        match_cpf = known_cpfs[best_match_index]
        matched_person = db.query(CommonPerson).filter(CommonPerson.cpf == match_cpf).first()
        
        if matched_person.is_wanted and matched_person.wanted_info:
            result = {
                "status": "wanted_alert",
                "cpf": matched_person.cpf,
                "full_name": matched_person.full_name,
                "crime": matched_person.wanted_info.crime,
                "risk_level": matched_person.wanted_info.risk_level
            }
        elif matched_person.is_employee:
            result = {
                "status": "employee_authorized",
                "cpf": matched_person.cpf,
                "full_name": matched_person.full_name
            }
        else:
            result = {
                "status": "common_cleared",
                "cpf": matched_person.cpf,
                "full_name": matched_person.full_name
            }
        db.close()
        return result
        
    db.close()
    return {"status": "unknown"}
    