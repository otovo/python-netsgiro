import string
from datetime import date

from hypothesis import given
from hypothesis import strategies as st

import netsgiro.records


def dates(min_value=date(1969, 1, 1), max_value=date(2068, 12, 31)):
    # The default min/max values are picked to match how Python converts
    # two-digit years to four-digit years. If Nets has specified any other
    # interpretation, the min/max here should be adjusted accordingly.
    return st.dates(min_value=min_value, max_value=max_value)


def digits(min_size=10, max_size=None):
    max_size = max_size or min_size
    return st.text(string.digits, min_size=min_size, max_size=max_size)


@given(tn=digits(7), dt=digits(8), dr=digits(8))
def test_transmission_start(tn, dt, dr):
    original = netsgiro.records.TransmissionStart(
        service_code=netsgiro.ServiceCode.NONE,
        transmission_number=tn,
        data_transmitter=dt,
        data_recipient=dr,
    )

    ocr = original.to_ocr()
    record = netsgiro.records.TransmissionStart.from_string(ocr)

    assert record.service_code == netsgiro.ServiceCode.NONE
    assert record.transmission_number == tn
    assert record.data_transmitter == dt
    assert record.data_recipient == dr


@given(
    nt=st.integers(min_value=0, max_value=99999999),
    nr=st.integers(min_value=0, max_value=99999999),
    ta=st.integers(min_value=0, max_value=99999999999999999),
    nd=dates(),
)
def test_transmission_end(nt, nr, ta, nd):
    original = netsgiro.records.TransmissionEnd(
        service_code=netsgiro.ServiceCode.NONE,
        num_transactions=nt,
        num_records=nr,
        total_amount=ta,
        nets_date=nd,
    )

    ocr = original.to_ocr()
    record = netsgiro.records.TransmissionEnd.from_string(ocr)

    assert record.service_code == netsgiro.ServiceCode.NONE
    assert record.num_transactions == nt
    assert record.num_records == nr
    assert record.total_amount == ta
    assert record.nets_date == nd


@given(an=digits(7), aa=digits(11), ai=digits(9))
def test_assignment_start_for_avtalegiro_payment_requests(an, aa, ai):
    original = netsgiro.records.AssignmentStart(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        assignment_type=netsgiro.AssignmentType.TRANSACTIONS,
        assignment_number=an,
        assignment_account=aa,
        agreement_id=ai,
    )

    ocr = original.to_ocr()
    record = netsgiro.records.AssignmentStart.from_string(ocr)

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.assignment_type == netsgiro.AssignmentType.TRANSACTIONS
    assert record.agreement_id == ai
    assert record.assignment_number == an
    assert record.assignment_account == aa


@given(an=digits(7), aa=digits(11))
def test_assignment_start_for_avtalegiro_agreements(an, aa):
    original = netsgiro.records.AssignmentStart(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        assignment_type=netsgiro.AssignmentType.AVTALEGIRO_AGREEMENTS,
        assignment_number=an,
        assignment_account=aa,
        agreement_id=None,
    )

    ocr = original.to_ocr()
    record = netsgiro.records.AssignmentStart.from_string(ocr)

    assert record.agreement_id is None
    assert record.assignment_number == an
    assert record.assignment_account == aa


@given(
    nt=st.integers(min_value=0, max_value=99999999),
    nr=st.integers(min_value=0, max_value=99999999),
    ta=st.integers(min_value=0, max_value=99999999999999999),
    nd1=dates(),
    nd2=dates(),
)
def test_assignment_end_for_avtalegiro_payment_requests(nt, nr, ta, nd1, nd2):
    original = netsgiro.records.AssignmentEnd(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        assignment_type=netsgiro.AssignmentType.TRANSACTIONS,
        num_transactions=nt,
        num_records=nr,
        total_amount=ta,
        nets_date_1=nd1,
        nets_date_2=nd2,
    )

    ocr = original.to_ocr()
    record = netsgiro.records.AssignmentEnd.from_string(ocr)

    assert record.num_transactions == nt
    assert record.num_records == nr
    assert record.total_amount == ta
    assert record.nets_date_earliest == nd1
    assert record.nets_date_latest == nd2


@given(
    nt=st.integers(min_value=0, max_value=99999999),
    nr=st.integers(min_value=0, max_value=99999999),
)
def test_assignment_end_for_avtalegiro_agreements(nt, nr):
    original = netsgiro.records.AssignmentEnd(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        assignment_type=netsgiro.AssignmentType.AVTALEGIRO_AGREEMENTS,
        num_transactions=nt,
        num_records=nr,
    )

    ocr = original.to_ocr()
    record = netsgiro.records.AssignmentEnd.from_string(ocr)

    assert record.num_transactions == nt
    assert record.num_records == nr


@given(
    tn=st.integers(min_value=0, max_value=9999999),
    nd=dates(),
    a=st.integers(min_value=0, max_value=99999999999999999),
    kid=digits(min_size=4, max_size=25),
    cid=digits(2),
    dc=st.integers(min_value=1, max_value=31),
    psn=st.integers(min_value=0, max_value=9),
    pssn=digits(5),
    sign=st.one_of(st.just('0'), st.just('-')),
)
def test_transaction_amount_item_1_for_ocr_giro_transactions(
    tn, nd, a, kid, cid, dc, psn, pssn, sign
):
    original = netsgiro.records.TransactionAmountItem1(
        service_code=netsgiro.ServiceCode.OCR_GIRO,
        transaction_type=netsgiro.TransactionType.FROM_GIRO_DEBITED_ACCOUNT,
        transaction_number=tn,
        nets_date=nd,
        amount=a,
        kid=kid,
        centre_id=cid,
        day_code=dc,
        partial_settlement_number=psn,
        partial_settlement_serial_number=pssn,
        sign=sign,
    )

    ocr = original.to_ocr()
    record = netsgiro.records.TransactionAmountItem1.from_string(ocr)

    assert record.transaction_number == tn
    assert record.nets_date == nd
    assert record.amount == a
    assert record.kid == kid

    assert record.centre_id == cid
    assert record.day_code == dc
    assert record.partial_settlement_number == psn
    assert record.partial_settlement_serial_number == pssn
    assert record.sign == sign


@given(
    tn=st.integers(min_value=0, max_value=9999999),
    nd=dates(),
    a=st.integers(min_value=0, max_value=99999999999999999),
    kid=digits(min_size=4, max_size=25),
)
def test_transaction_amount_item_1_for_avtalegiro_payment_requests(
    tn, nd, a, kid
):
    original = netsgiro.records.TransactionAmountItem1(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        transaction_type=(
            netsgiro.TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION
        ),
        transaction_number=tn,
        nets_date=nd,
        amount=a,
        kid=kid,
    )

    ocr = original.to_ocr()
    record = netsgiro.records.TransactionAmountItem1.from_string(ocr)

    assert record.transaction_number == tn
    assert record.nets_date == nd
    assert record.amount == a
    assert record.kid == kid


@given(tn=st.integers(min_value=0, max_value=9999999), pn=st.text(max_size=10))
def test_transaction_amount_item_2_for_avtalegiro_payment_request(tn, pn):
    original = netsgiro.records.TransactionAmountItem2(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        transaction_type=(
            netsgiro.TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION
        ),
        transaction_number=tn,
        reference=None,
        payer_name=pn,
    )

    ocr = original.to_ocr()
    record = netsgiro.records.TransactionAmountItem2.from_string(ocr)

    assert record.transaction_number == tn
    assert record.payer_name == original.payer_name


@given(
    tn=st.integers(min_value=0, max_value=9999999),
    ref=digits(9),
    fn=digits(10),
    bd=dates(),
    da=digits(11),
)
def test_transaction_amount_item_2_for_ocr_giro_transactions(
    tn, ref, fn, bd, da
):
    original = netsgiro.records.TransactionAmountItem2(
        service_code=netsgiro.ServiceCode.OCR_GIRO,
        transaction_type=(netsgiro.TransactionType.FROM_GIRO_DEBITED_ACCOUNT),
        transaction_number=tn,
        reference=ref,
        form_number=fn,
        bank_date=bd,
        debit_account=da,
    )

    ocr = original.to_ocr()
    record = netsgiro.records.TransactionAmountItem2.from_string(ocr)

    assert record.transaction_number == tn
    assert record.form_number == fn
    assert record.payer_name is None
    assert record.reference == ref
    assert record.bank_date == bd
    assert record.debit_account == da


@given(
    tn=st.integers(min_value=0, max_value=9999999), text=st.text(max_size=40)
)
def test_transaction_amount_item_3_for_ocr_giro_transactions(tn, text):
    original = netsgiro.records.TransactionAmountItem3(
        service_code=netsgiro.ServiceCode.OCR_GIRO,
        transaction_type=(netsgiro.TransactionType.PURCHASE_WITH_TEXT),
        transaction_number=tn,
        text=text,
    )

    ocr = original.to_ocr()
    record = netsgiro.records.TransactionAmountItem3.from_string(ocr)

    assert record.transaction_number == tn
    assert record.text == original.text


@given(
    tn=st.integers(min_value=0, max_value=9999999),
    ln=st.integers(min_value=1, max_value=42),
    cn=st.integers(min_value=1, max_value=2),
    text=st.text(min_size=40, max_size=40),
)
def test_transaction_specification_for_avtalegiro_payment_request(
    tn, ln, cn, text
):
    original = netsgiro.records.TransactionSpecification(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        transaction_type=(
            netsgiro.TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION
        ),
        transaction_number=tn,
        line_number=ln,
        column_number=cn,
        text=text,
    )

    ocr = original.to_ocr()
    record = netsgiro.records.TransactionSpecification.from_string(ocr)

    assert record.transaction_number == tn
    assert record.line_number == ln
    assert record.column_number == cn
    assert len(record.text) == 40
    assert record.text == original.text


@given(
    tn=st.integers(min_value=0, max_value=9999999),
    kid=digits(min_size=4, max_size=25),
    n=st.booleans(),
)
def test_avtalegiro_agreement(tn, kid, n):
    original = netsgiro.records.AvtaleGiroAgreement(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        transaction_type=(netsgiro.TransactionType.AVTALEGIRO_AGREEMENT),
        transaction_number=tn,
        registration_type=(
            netsgiro.AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT
        ),
        kid=kid,
        notify=n,
    )

    ocr = original.to_ocr()
    record = netsgiro.records.AvtaleGiroAgreement.from_string(ocr)

    assert record.transaction_number == tn
    assert record.kid == kid
    assert record.notify == n
