from datetime import date

from hypothesis import given
from hypothesis import strategies as st

import netsgiro.records


def dates(min_value=date(1969, 1, 1), max_value=date(2068, 12, 31)):
    # The default min/max values are picked to match how Python converts
    # two-digit years to four-digit years. If Nets has specified any other
    # interpretation, the min/max here should be adjusted accordingly.
    return st.dates(min_value=min_value, max_value=max_value)


def digits(num_digits=10):
    max_value = 10**num_digits - 1
    return (
        st.integers(min_value=0, max_value=max_value)
        .map(lambda v: '{value:0{num_digits}}'.format(
            num_digits=num_digits, value=v)))


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
    nt=st.integers(min_value=0),
    nr=st.integers(min_value=0),
    ta=st.integers(min_value=0),
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
    nt=st.integers(min_value=0),
    nr=st.integers(min_value=0),
    ta=st.integers(min_value=0),
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
    nt=st.integers(min_value=0),
    nr=st.integers(min_value=0),
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
