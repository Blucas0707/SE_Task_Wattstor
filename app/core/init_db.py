from app.core.database import Base, engine


def main():
    print('Creating all tables...')
    Base.metadata.create_all(bind=engine)
    print('All tables created successfully.')


if __name__ == '__main__':
    main()
