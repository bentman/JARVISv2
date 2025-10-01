from app.services.privacy_service import privacy_service, DataClassification


def test_privacy_classification_email_personal():
    text = "Contact me at user@example.com"
    classification = privacy_service.classify_data(text)
    assert classification == DataClassification.PERSONAL


def test_privacy_classification_credit_card_sensitive():
    text = "My card is 4242 4242 4242 4242"
    classification = privacy_service.classify_data(text)
    assert classification == DataClassification.SENSITIVE
