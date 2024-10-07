from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)


class Alignment(enum.Enum):
    strongly_aligned = "strongly_aligned"
    aligned = "aligned"
    misaligned = "misaligned"
    strongly_misaligned = "strongly_misaligned"

class NodeType(enum.Enum):
    company = "company"
    category = "category"
    product = "product"

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(NodeType), nullable=False)

    parent_id = Column(Integer, ForeignKey('nodes.id'), nullable=True)
    children = relationship("Node", backref="parent", remote_side=[id])

    revenue = Column(Float, nullable=True)  # Only for product nodes (leaves)
    alignment = Column(Enum(Alignment), nullable=True)  # Optional for all nodes

    def __repr__(self):
        return f"<Node(name={self.name}, type={self.type}, parent_id={self.parent_id})>"
    

