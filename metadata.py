from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

config = dotenv_values(".env")

USERNAME = config["USERNAME"]
PASSWORD = config["PASSWORD"]
URL_DATABASE = config["URL_DATABASE"]
DB_NAME = config["DB_NAME"]
SUPERSET_SECRET_KEY = config["SUPERSET_SECRET_KEY"]
URI = f'postgresql://{USERNAME}:{PASSWORD}@{URL_DATABASE}:5432/JobPostManagement'

engine = create_engine(URI)
Session = sessionmaker(bind=engine)
session = Session()

cities = [
    'Hà Nội',
    'Hồ Chí Minh',
    'Bà Rịa-Vũng Tàu',
    'Đà Nẵng',
    'Khánh Hòa',
    'Hải Dương',
    'Vĩnh Phúc',
    'Hà Nam',
    'Hải Phòng',
    'HN',
    'Hanoi',
    'Ha Noi',
    'Ho Chi Minh',
    'Da Nang',
    'Lâm Đồng',
    'Cần Thơ',
    'Đồng Nai',
    'Bắc Ninh',
    'Phú Yên',
    'Khánh Hoà',
    'Bình Dương',
    'Ninh Bình',
    'Đắk Lắk',
    'Bình Thuận',
    'Phú Thọ',
    'Kiên Giang',
    'Nghệ An',
    'Long An',
    'Sóc Trăng',
    'Ninh Thuận',
    'Hưng Yên',
    'Thanh Hoá',
    'Tiền Giang',
    'Bình Định',
    'Quảng Ninh',
    'Huế',
    'Quảng Nam',
    'Thái Nguyên',
    'Kon Tum',
    'Miền Nam',
    'Nước Ngoài',
    'Toàn Quốc',
    'Miền Bắc',
    'Miền Trung',
    'Hoà Bình',
    'Đồng Tháp',
]

north_region = [
    'Hà Nội',
    'HN',
    'Hanoi',
    'Ha Noi',
    'Hải Dương',
    'Vĩnh Phúc',
    'Hà Nam',
    'Hải Phòng',
    'Bắc Ninh',
    'Ninh Bình',
    'Phú Thọ',
    'Hưng Yên',
    'Thanh Hoá',
    'Thái Nguyên',
    'Hoà Bình',
    'Quảng Ninh'
]

central_region = [
    'Đà Nẵng',
    'Da Nang',
    'Khánh Hòa',
    'Khánh Hoà',
    'Phú Yên',
    'Ninh Thuận',
    'Bình Định',
    'Huế',
    'Quảng Nam',
    'Nghệ An',
    'Kon Tum',
    'Lâm Đồng',
    'Đắk Lắk'
]

sourth_region = [
    'Hồ Chí Minh',
    'Ho Chi Minh',
    'Bà Rịa-Vũng Tàu',
    'Cần Thơ',
    'Đồng Nai',
    'Bình Dương',
    'Bình Thuận',
    'Kiên Giang',
    'Long An',
    'Sóc Trăng',
    'Tiền Giang',
    'Đồng Tháp',
]