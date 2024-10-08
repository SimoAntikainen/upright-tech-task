from sqlalchemy.orm import Session
from .models import User, Node, NodeType, Alignment
from .database import SessionLocal

def init():
    db: Session = SessionLocal()

    # Create a user
    user = User(name="admin", email="admin@example.com")
    db.add(user)
    db.commit()
    db.refresh(user)

    # First Company
    company_1 = Node(name="TechCorp", type=NodeType.company, alignment=Alignment.strongly_aligned)
    db.add(company_1)
    db.commit()
    db.refresh(company_1)

    # Categories under TechCorp
    electronics_1 = Node(name="Electronics", type=NodeType.category, parent_id=company_1.id, alignment=Alignment.aligned, company_id=company_1.id)
    fashion_1 = Node(name="Fashion", type=NodeType.category, parent_id=company_1.id, alignment=Alignment.aligned, company_id=company_1.id)
    db.add_all([electronics_1, fashion_1])
    db.commit()
    db.refresh(electronics_1)
    db.refresh(fashion_1)

    # Subcategories under Electronics (TechCorp)
    phones_1 = Node(name="Mobile Phones", type=NodeType.category, parent_id=electronics_1.id, alignment=Alignment.strongly_aligned, company_id=company_1.id)
    laptops_1 = Node(name="Laptops", type=NodeType.category, parent_id=electronics_1.id, alignment=Alignment.misaligned, company_id=company_1.id)
    db.add_all([phones_1, laptops_1])
    db.commit()
    db.refresh(phones_1)
    db.refresh(laptops_1)

    # Subcategories under Fashion (TechCorp)
    mens_wear_1 = Node(name="Men's Wear", type=NodeType.category, parent_id=fashion_1.id, alignment=Alignment.aligned, company_id=company_1.id)
    womens_wear_1 = Node(name="Women's Wear", type=NodeType.category, parent_id=fashion_1.id, alignment=Alignment.strongly_aligned, company_id=company_1.id)
    db.add_all([mens_wear_1, womens_wear_1])
    db.commit()
    db.refresh(mens_wear_1)
    db.refresh(womens_wear_1)

    # Products under Mobile Phones (TechCorp)
    iphone_1 = Node(name="iPhone 13", type=NodeType.product, parent_id=phones_1.id, revenue=999.99, alignment=Alignment.aligned, company_id=company_1.id)
    galaxy_1 = Node(name="Samsung Galaxy S21", type=NodeType.product, parent_id=phones_1.id, revenue=799.99, alignment=Alignment.aligned, company_id=company_1.id)
    db.add_all([iphone_1, galaxy_1])
    db.commit()

    # Products under Laptops (TechCorp)
    macbook_1 = Node(name="MacBook Pro", type=NodeType.product, parent_id=laptops_1.id, revenue=1299.99, alignment=Alignment.strongly_aligned, company_id=company_1.id)
    dell_xps_1 = Node(name="Dell XPS 13", type=NodeType.product, parent_id=laptops_1.id, revenue=999.99, alignment=Alignment.misaligned, company_id=company_1.id)
    db.add_all([macbook_1, dell_xps_1])
    db.commit()

    # Products under Men's Wear (TechCorp)
    tshirt_1 = Node(name="T-Shirt", type=NodeType.product, parent_id=mens_wear_1.id, revenue=19.99, alignment=Alignment.strongly_misaligned, company_id=company_1.id)
    jeans_1 = Node(name="Jeans", type=NodeType.product, parent_id=mens_wear_1.id, revenue=49.99, alignment=Alignment.misaligned, company_id=company_1.id)
    db.add_all([tshirt_1, jeans_1])
    db.commit()

    # Products under Women's Wear (TechCorp)
    dress_1 = Node(name="Dress", type=NodeType.product, parent_id=womens_wear_1.id, revenue=79.99, alignment=Alignment.aligned, company_id=company_1.id)
    handbag_1 = Node(name="Handbag", type=NodeType.product, parent_id=womens_wear_1.id, revenue=150.00, alignment=Alignment.strongly_aligned, company_id=company_1.id)
    db.add_all([dress_1, handbag_1])
    db.commit()

    # Second Company
    company_2 = Node(name="MyCompany", type=NodeType.company, alignment=Alignment.strongly_aligned)
    db.add(company_2)
    db.commit()
    db.refresh(company_2)

    # Categories under MyCompany
    electronics_2 = Node(name="Electronics", type=NodeType.category, parent_id=company_2.id, alignment=Alignment.aligned, company_id=company_2.id)
    fashion_2 = Node(name="Fashion", type=NodeType.category, parent_id=company_2.id, alignment=Alignment.aligned, company_id=company_2.id)
    db.add_all([electronics_2, fashion_2])
    db.commit()

    # Products under Electronics (MyCompany)
    phone_2 = Node(name="Smartphone", type=NodeType.product, parent_id=electronics_2.id, revenue=699.99, alignment=Alignment.aligned, company_id=company_2.id)
    laptop_2 = Node(name="Laptop", type=NodeType.product, parent_id=electronics_2.id, revenue=999.99, alignment=Alignment.strongly_aligned, company_id=company_2.id)
    db.add_all([phone_2, laptop_2])
    db.commit()

    # Products under Fashion (MyCompany)
    tshirt_2 = Node(name="T-shirt", type=NodeType.product, parent_id=fashion_2.id, revenue=19.99, alignment=Alignment.misaligned, company_id=company_2.id)
    db.add(tshirt_2)
    db.commit()

    db.close()

if __name__ == "__main__":
    print("hello")
    init()
