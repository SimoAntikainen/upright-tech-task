from sqlalchemy.orm import Session
from .models import User, Node, NodeType, Alignment
from .database import SessionLocal

def init():
    db: Session = SessionLocal()

    user = User(name="admin", email="admin@example.com")
    db.add(user)
    db.commit()
    db.refresh(user)

    company = Node(name="TechCorp", type=NodeType.company, alignment=Alignment.strongly_aligned)
    db.add(company)
    db.commit()
    db.refresh(company)

    electronics = Node(name="Electronics", type=NodeType.category, parent_id=company.id, alignment=Alignment.aligned)
    fashion = Node(name="Fashion", type=NodeType.category, parent_id=company.id, alignment=Alignment.aligned)
    db.add_all([electronics, fashion])
    db.commit()
    db.refresh(electronics)
    db.refresh(fashion)

    phones = Node(name="Mobile Phones", type=NodeType.category, parent_id=electronics.id, alignment=Alignment.strongly_aligned)
    laptops = Node(name="Laptops", type=NodeType.category, parent_id=electronics.id, alignment=Alignment.misaligned)
    db.add_all([phones, laptops])
    db.commit()
    db.refresh(phones)
    db.refresh(laptops)

    mens_wear = Node(name="Men's Wear", type=NodeType.category, parent_id=fashion.id, alignment=Alignment.aligned)
    womens_wear = Node(name="Women's Wear", type=NodeType.category, parent_id=fashion.id, alignment=Alignment.strongly_aligned)
    db.add_all([mens_wear, womens_wear])
    db.commit()
    db.refresh(mens_wear)
    db.refresh(womens_wear)

    iphone = Node(name="iPhone 13", type=NodeType.product, parent_id=phones.id, revenue=999.99, alignment=Alignment.aligned)
    galaxy = Node(name="Samsung Galaxy S21", type=NodeType.product, parent_id=phones.id, revenue=799.99, alignment=Alignment.aligned)
    db.add_all([iphone, galaxy])
    db.commit()

    macbook = Node(name="MacBook Pro", type=NodeType.product, parent_id=laptops.id, revenue=1299.99, alignment=Alignment.strongly_aligned)
    dell_xps = Node(name="Dell XPS 13", type=NodeType.product, parent_id=laptops.id, revenue=999.99, alignment=Alignment.misaligned)
    db.add_all([macbook, dell_xps])
    db.commit()

    tshirt = Node(name="T-Shirt", type=NodeType.product, parent_id=mens_wear.id, revenue=19.99, alignment=Alignment.strongly_misaligned)
    jeans = Node(name="Jeans", type=NodeType.product, parent_id=mens_wear.id, revenue=49.99, alignment=Alignment.misaligned)
    db.add_all([tshirt, jeans])
    db.commit()

    dress = Node(name="Dress", type=NodeType.product, parent_id=womens_wear.id, revenue=79.99, alignment=Alignment.aligned)
    handbag = Node(name="Handbag", type=NodeType.product, parent_id=womens_wear.id, revenue=150.00, alignment=Alignment.strongly_aligned)
    db.add_all([dress, handbag])
    db.commit()

    company = Node(name="MyCompany", type=NodeType.company, alignment=Alignment.strongly_aligned)
    db.add(company)
    db.commit()
    db.refresh(company)

    electronics = Node(name="Electronics", type=NodeType.category, parent_id=company.id, alignment=Alignment.aligned)
    fashion = Node(name="Fashion", type=NodeType.category, parent_id=company.id, alignment=Alignment.aligned)
    db.add_all([electronics, fashion])
    db.commit()

    phone = Node(name="Smartphone", type=NodeType.product, parent_id=electronics.id, revenue=699.99, alignment=Alignment.aligned)
    laptop = Node(name="Laptop", type=NodeType.product, parent_id=electronics.id, revenue=999.99, alignment=Alignment.strongly_aligned)
    tshirt = Node(name="T-shirt", type=NodeType.product, parent_id=fashion.id, revenue=19.99, alignment=Alignment.misaligned)
    
    db.add_all([phone, laptop, tshirt])
    db.commit()

    db.close()

if __name__ == "__main__":
    print("hello")
    init()
