"""Exercise local image routes and ReportLab interoperability with dummy data."""
import base64
import io

from bs4 import BeautifulSoup
from PIL import Image
import pytest
from reportlab.lib.utils import ImageReader

from app import create_app, db
from app.models.inventory import InventoryItem
from app.models.user import User
from app.routes import inventory
from config import Config


class ImageTestConfig(Config):
    TESTING = True
    SECRET_KEY = 'image-test-secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


@pytest.fixture
def image_client():
    app = create_app(ImageTestConfig)
    with app.test_client() as client, app.app_context():
        db.create_all()
        try:
            user = User(username='imageuser', email='image@example.invalid')
            user.set_password('image-test-password')
            item = InventoryItem(name='Dummy cable', tracking_id='TC-TEST0001')
            db.session.add_all([user, item])
            db.session.commit()
            form = client.get('/login')
            assert form.status_code == 200
            token = BeautifulSoup(form.data, 'html.parser').find(
                'input', {'name': 'csrf_token'})['value']
            login = client.post('/login', data={
                'username': user.username,
                'password': 'image-test-password',
                'csrf_token': token,
            })
            assert login.status_code == 302
            with client.session_transaction() as session:
                assert session['_user_id'] == str(user.id)
            yield client, item.id
        finally:
            db.session.remove()
            db.drop_all()


def png_from_response(response, alt):
    assert response.status_code == 200
    image = BeautifulSoup(response.data, 'html.parser').find('img', alt=alt)
    assert image is not None
    prefix, encoded = image['src'].split(',', 1)
    assert prefix == 'data:image/png;base64'
    data = base64.b64decode(encoded, validate=True)
    assert data.startswith(b'\x89PNG\r\n\x1a\n')
    with Image.open(io.BytesIO(data)) as decoded:
        assert decoded.format == 'PNG'
        decoded.verify()
    with Image.open(io.BytesIO(data)) as decoded:
        decoded.load()
        assert decoded.width > 100
        assert decoded.height > 100
        assert decoded.convert('L').getextrema() == (0, 255)
    return data


def test_item_view_generates_barcode_and_qr_png(image_client):
    client, item_id = image_client
    response = client.get(f'/item/{item_id}/view')
    barcode = png_from_response(response, 'Barcode')
    qr = png_from_response(response, 'QR Code')
    assert barcode != qr
    with Image.open(io.BytesIO(qr)) as decoded:
        assert decoded.width == decoded.height


def test_print_label_generates_barcode_png(image_client):
    client, item_id = image_client
    response = client.get(f'/item/{item_id}/label')
    png_from_response(response, 'Barcode')
    assert b'TC-TEST0001' in response.data


def test_reportlab_embeds_route_images_in_memory(image_client):
    # inventory imports ReportLab but currently has no PDF-producing route.
    client, item_id = image_client
    response = client.get(f'/item/{item_id}/view')
    output = io.BytesIO()
    pdf = inventory.canvas.Canvas(output, pageCompression=0,
                                  pagesize=(4 * inventory.inch, 2 * inventory.inch))
    for index, alt in enumerate(('Barcode', 'QR Code')):
        data = png_from_response(response, alt)
        reader = ImageReader(io.BytesIO(data))
        assert min(reader.getSize()) > 100
        pdf.drawImage(reader, index * 2 * inventory.inch, 0,
                      width=2 * inventory.inch, height=2 * inventory.inch)
    pdf.showPage()
    pdf.save()
    document = output.getvalue()
    assert document.startswith(b'%PDF-')
    assert document.rstrip().endswith(b'%%EOF')
    assert document.count(b'/Subtype /Image') == 2
    assert b'/Count 1' in document
