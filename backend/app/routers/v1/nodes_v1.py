from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case
from typing import List
from app.models import Node, NodeType, Alignment
from app.database import SessionLocal
from pydantic import BaseModel
from typing import Optional


router = APIRouter(
    prefix="/v1/nodes", 
    tags=["nodes_v1"]
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class NodeBase(BaseModel):
    name: str
    type: NodeType
    alignment: Optional[Alignment] = None  # Alignment is optional for all nodes

class NodeCreate(NodeBase):
    parent_id: Optional[int] = None  # Parent ID is optional for top-level nodes
    revenue: Optional[float] = None  # Revenue is optional and only relevant for product nodes

class NodeResponse(NodeBase):
    id: int
    parent_id: Optional[int] = None
    revenue: Optional[float] = None  # Revenue is only relevant for product nodes
    company_id: Optional[int] = None

    class Config:
        orm_mode = True  # Enable ORM mode to work with SQLAlchemy models


@router.get("/", response_model=List[NodeResponse])
def get_all_nodes(db: Session = Depends(get_db)):
    nodes = db.query(Node).all()
    print(nodes)
    return nodes


@router.get("/{node_id}", response_model=NodeResponse)
def get_node(node_id: int, db: Session = Depends(get_db)):
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


"""@router.post("/", response_model=NodeResponse)
def create_node(node: NodeCreate, db: Session = Depends(get_db)):
    new_node = Node(name=node.name, type=node.type, parent_id=node.parent_id)
    db.add(new_node)
    db.commit()
    db.refresh(new_node)
    return new_node"""

def get_effective_alignment_from_parent(parent_id: Optional[int], db: Session) -> Optional[Alignment]:
    if not parent_id:
        return None
    
    parent = db.query(Node).filter(Node.id == parent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent node not found")
    
    if parent.alignment is not None:
        return parent.alignment
    
    # Recursively check the parent's parent for alignment
    return get_effective_alignment_from_parent(parent.parent_id, db)


"""@router.post("/", response_model=NodeResponse)
def create_node(node: NodeCreate, db: Session = Depends(get_db)):
    # Check if alignment is provided; if not, inherit it from the parent
    alignment = node.alignment
    if alignment is None and node.parent_id is not None:
        alignment = get_effective_alignment_from_parent(node.parent_id, db)

    # Set revenue to None if the node is a category
    revenue = None if node.type == NodeType.category or node.type == NodeType.company  else node.revenue

    # Create the new node with inherited or provided alignment
    new_node = Node(
        name=node.name,
        type=node.type,
        parent_id=node.parent_id,
        alignment=alignment,
        revenue=revenue
    )

    db.add(new_node)
    db.commit()
    db.refresh(new_node)
    return new_node"""

@router.post("/", response_model=NodeResponse)
def create_node(node: NodeCreate, db: Session = Depends(get_db)):
    # Check if alignment is provided; if not, inherit it from the parent
    alignment = node.alignment
    company_id = None

    if node.parent_id is not None:
        # Get the parent node to derive company_id and alignment if necessary
        parent_node = db.query(Node).filter(Node.id == node.parent_id).first()
        if not parent_node:
            raise HTTPException(status_code=404, detail="Parent node not found")
        
        if parent_node.type == NodeType.product:
            raise HTTPException(status_code=403, detail="Cannot set product as parent to product")
        
        if parent_node.type == NodeType.company and node.type == NodeType.company:
            raise HTTPException(status_code=403, detail="Cannot set company as parent to company")
        
        # Inherit company_id from the parent if the node is not a company
        if parent_node.type == NodeType.company:
            company_id = parent_node.id  # The company ID is the parent ID if the parent is a company
        else:
            company_id = parent_node.company_id  # Otherwise, inherit the company ID from the parent


        # Inherit alignment if it's not provided
        if alignment is None:
            alignment = get_effective_alignment_from_parent(node.parent_id, db)

    # Set revenue to None if the node is a category or company
    revenue = None if node.type == NodeType.category or node.type == NodeType.company else node.revenue

    # Create the new node with inherited or provided alignment and company_id
    new_node = Node(
        name=node.name,
        type=node.type,
        parent_id=node.parent_id,
        alignment=alignment,
        revenue=revenue,
        company_id=company_id 
    )

    db.add(new_node)
    db.commit()
    db.refresh(new_node)
    return new_node



@router.put("/{node_id}", response_model=NodeResponse)
def update_node(node_id: int, updated_node: NodeCreate, db: Session = Depends(get_db)):
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # Set revenue to None if the node is a category
    revenue = None if node.type == NodeType.category or node.type == NodeType.company  else node.revenue
    
    node.name = updated_node.name
    node.type = updated_node.type
    node.parent_id = updated_node.parent_id
    node.alignment=updated_node.alignment,
    node.revenue=revenue
    
    db.commit()
    db.refresh(node)
    return node


@router.delete("/{node_id}")
def delete_node(node_id: int, db: Session = Depends(get_db)):
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    db.delete(node)
    db.commit()
    return {"detail": "Node deleted successfully"}



def get_all_subcategories(category_id: int, db: Session) -> List[Node]:
    subcategories = db.query(Node).filter(Node.parent_id == category_id, Node.type == NodeType.category).all()
    all_categories = subcategories[:]
    for subcategory in subcategories:
        all_categories.extend(get_all_subcategories(subcategory.id, db))
    return all_categories

def get_all_products_from_company(company_id: int, db: Session) -> List[Node]:
    products = []
    categories = db.query(Node).filter(Node.parent_id == company_id, Node.type == NodeType.category).all()

    for category in categories:
        products.extend(get_all_products_from_category(category.id, db))
    
    return products

def get_all_products_from_category(category_id: int, db: Session) -> List[Node]:
    products = db.query(Node).filter(Node.parent_id == category_id, Node.type == NodeType.product).all()

    subcategories = db.query(Node).filter(Node.parent_id == category_id, Node.type == NodeType.category).all()

    for subcategory in subcategories:
        products.extend(get_all_products_from_category(subcategory.id, db))

    return products

@router.get("/company/{company_id}/products", response_model=List[NodeResponse])
def get_all_products_under_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Node).filter(Node.id == company_id, Node.type == NodeType.company).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    products = get_all_products_from_company(company.id, db)
    
    if not products:
        raise HTTPException(status_code=404, detail="No products found for this company")
    
    return products


@router.get("/company/{company_id}/categories", response_model=List[NodeResponse])
def get_categories_under_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Node).filter(Node.id == company_id, Node.type == NodeType.company).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    categories = db.query(Node).filter(Node.parent_id == company.id, Node.type == NodeType.category).all()
    all_categories = categories[:]
    for category in categories:
        all_categories.extend(get_all_subcategories(category.id, db))

    if not all_categories:
        raise HTTPException(status_code=404, detail="No categories found for this company")

    return all_categories


@router.get("/category/{category_id}/products", response_model=List[NodeResponse])
def get_products_under_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Node).filter(Node.id == category_id, Node.type == NodeType.category).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    products = get_all_products_from_category(category.id, db)

    if not products:
        raise HTTPException(status_code=404, detail="No products found for this category")

    return products


def calculate_alignment_score(products: List[Node]) -> float:
    total_revenue = 0
    weighted_score = 0

    alignment_scores = {
        Alignment.strongly_aligned: 2,
        Alignment.aligned: 1,
        Alignment.misaligned: -1,
        Alignment.strongly_misaligned: -2
    }

    for product in products:
        if product.revenue is None or product.alignment is None:
            continue 

        alignment_score = alignment_scores.get(product.alignment, 0)

        weighted_score += alignment_score * product.revenue

        total_revenue += product.revenue

    if total_revenue == 0:
        return 0.0  

    alignment_score = weighted_score / total_revenue
    return alignment_score


class CompanyAlignmentResponse(BaseModel):
    alignment_score: float
    products: List[NodeResponse]

@router.get("/company/{company_id}/products/alignment", response_model=CompanyAlignmentResponse)
def get_company_alignment_score(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Node).filter(Node.id == company_id, Node.type == NodeType.company).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    products = get_all_products_from_company(company.id, db)

    if not products:
        raise HTTPException(status_code=404, detail="No products found for this company")

    alignment_score = calculate_alignment_score(products)

    return {
        "alignment_score": alignment_score,
        "products": products
    }

def get_all_products_from_company_optimized(company_id: int, db: Session) -> List[Node]:

    products = db.query(Node).filter(
        Node.company_id == company_id,
        Node.type == NodeType.product
    ).all()

    if not products:
        raise HTTPException(status_code=404, detail="No products found for this company")

    return products

@router.get("/company/{company_id}/products/alignmentOptimized", response_model=CompanyAlignmentResponse)
def get_company_alignment_score_optimized(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Node).filter(Node.id == company_id, Node.type == NodeType.company).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    products = get_all_products_from_company_optimized(company.id, db)

    if not products:
        raise HTTPException(status_code=404, detail="No products found for this company")

    alignment_score = calculate_alignment_score(products)

    return {
        "alignment_score": alignment_score,
        "products": products
    }



def get_session_local():
    yield SessionLocal()


class CompanyAlignmentDBResponse(BaseModel):
    alignment_score: float

@router.get("/company/{company_id}/products/alignmentDatabaseAggregation", response_model=CompanyAlignmentDBResponse)
def get_company_alignment_score_with_database_aggregation(company_id: int, db: Session = Depends(get_session_local)):
    # Step 1: Calculate total weighted score and total revenue using SQL aggregation
    result = db.query(
        func.sum(
            case(
                (Node.alignment == Alignment.strongly_aligned, 2),
                (Node.alignment == Alignment.aligned, 1),
                (Node.alignment == Alignment.misaligned, -1),
                (Node.alignment == Alignment.strongly_misaligned, -2),
                else_=0  # Default value if no condition matches
            ) * Node.revenue
        ).label('weighted_score'),
        func.sum(Node.revenue).label('total_revenue')
    ).filter(
        Node.company_id == company_id,
        Node.type == NodeType.product,
        Node.revenue.isnot(None),
        Node.alignment.isnot(None)
    ).first()

    print()

    # Step 2: Get the weighted score and total revenue from the query result
    weighted_score = result.weighted_score
    total_revenue = result.total_revenue

    if total_revenue is None or total_revenue == 0:
        raise HTTPException(status_code=400, detail="No revenue data available for products")

    # Step 3: Calculate the final alignment score
    alignment_score = weighted_score / total_revenue if weighted_score else 0

    return {
        "alignment_score": alignment_score,
    }


