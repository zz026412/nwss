from contextlib import contextmanager
from marshmallow import ValidationError
import pytest
import jsonschema

from nwss.utils import get_future_date


def test_valid_data(schema, valid_data):
    schema.load(valid_data)


def test_invalid_data(schema, invalid_data):
    with pytest.raises(ValidationError):
        schema.load(invalid_data)


@contextmanager
def does_not_raise():
    yield


def test_json_schema(valid_json, json_schema):
    # cannot figure out how to make
    # the jsonschema-marshmallow to allow an array
    for field in valid_json:
        jsonschema.validate(instance=field, schema=json_schema)

        # make the field invalid
        field.update({
            'sample_location': 'upstream',
            'sample_location_specify': None
        })

        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=field, schema=json_schema)


def update_data(input, valid_data):
    data = valid_data.pop(0)
    data.update(**input)
    return [data]


def test_valid_json_schema(valid_json, json_schema):
    # should not raise an exception
    jsonschema.validate(instance=valid_json, schema=json_schema)


@pytest.mark.parametrize(
    'input,expect',
    [
        (
            {
                'sample_location': 'upstream',
                'sample_location_specify': None
            },
            pytest.raises(jsonschema.ValidationError)
        ),
        (
            {
                'pretreatment': 'yes',
                'pretreatment_specify': None
            },
            pytest.raises(jsonschema.ValidationError)
        ),
        (
            {
                'sample_matrix': 'raw wastewater',
                'flow_rate': None
            },
            pytest.raises(jsonschema.ValidationError)
        ),
        (
            {
                'inhibition_detect': 'yes',
                'inhibition_adjust': None
            },
            pytest.raises(jsonschema.ValidationError)
        ),
        (
            {
                'inhibition_detect': 'not tested',
                'inhibition_method': None
            },
            pytest.raises(jsonschema.ValidationError)
        )
    ]
)
def test_invalid_sample_location(valid_json, json_schema, input, expect):
    data = update_data(input, valid_json)
    with expect:
        jsonschema.validate(instance=data, schema=json_schema)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'reporting_jurisdiction': 'CA'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'reporting_jurisdiction': 'ca'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'reporting_jurisdiction': 'IL'
            },
            does_not_raise(),
            None
        ),
        (
            {'reporting_jurisdiction': 'AL'},
            does_not_raise(),
            None
        ),
        (
            {'reporting_jurisdiction': 'CAA'},
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {'reporting_jurisdiction': 'I'},
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {'reporting_jurisdiction': 'AA'},
            pytest.raises(ValidationError),
            'Must be one of:'
        )
    ]
)
def test_reporting_jurisdictions(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)
    with expect as e:
        schema.load(list(data))

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'county_names': 'Los Angeles',
                'other_jurisdiction': ''
            },
            does_not_raise(),
            None
        ),
        (
            {
                'county_names': 'Los Angeles, San Diego',
                'other_jurisdiction': ''
            },
            does_not_raise(),
            None
        ),
        (
            {
                'county_names': '',
                'other_jurisdiction': 'Calabasas'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'county_names': '',
                'other_jurisdiction': ''
            },
            pytest.raises(ValidationError),
            'Either county_names or other_jurisdiction must have a value.'
        )
    ]
)
def test_county_jurisdiction(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'sample_location': 'wwtp',
                'sample_location_specify': ''
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sample_location': 'WWTP',  # case insensitive
                'sample_location_specify': ''
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sample_location': 'wwtp',
                'sample_location_specify': 'details'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sample_location': 'upstream',
                'sample_location_specify': 'location details'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sample_location': 'upstream',
                'sample_location_specify': ''
            },
            pytest.raises(ValidationError),
            'An "upstream" sample_location must'
        ),
        (
            {
                'sample_location': 'invalid location',
                'sample_location_specify': 'location details'
            },
            pytest.raises(ValidationError),
            'Must be one of: wwtp, upstream.'
        ),
        (
            {
                'sample_location': '',
                'sample_location_specify': ''
            },
            pytest.raises(ValidationError),
            'Field may not be null.'
        )
    ]
)
def test_sample_location_valid(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
               'institution_type': 'long term care - nursing home'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'institution_type': 'child day care'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'institution_type': 'CHILD DAY CARE'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'institution_type': 'not institution specific'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'institution_type': ''
            },
            pytest.raises(ValidationError),
            'Field may not be null.'
        ),
        (
            {
                'institution_type': 'child day car'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'institution_type': 'none'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        )
    ]
)
def test_institution_type(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'epaid': 'AL0042234'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'epaid': 'ca2343454'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'epaid': None
            },
            does_not_raise(),
            None
        ),
        (
            {
                'epaid': 'CA1123'
            },
            pytest.raises(ValidationError),
            'String does not match expected pattern.'
        ),
        (
            {
                'epaid': 'CAA112323'
            },
            pytest.raises(ValidationError),
            'String does not match expected pattern.'
        ),
        (
            {
                'epaid': '0042234AL'
            },
            pytest.raises(ValidationError),
            'String does not match expected pattern.'
        )
    ]
)
def test_epaid_valid(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'wwtp_jurisdiction': 'AL'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'wwtp_jurisdiction': 'IL'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'wwtp_jurisdiction': 'MO'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'wwtp_jurisdiction': 'ALL'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'wwtp_jurisdiction': 'ILL'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'wwtp_jurisdiction': 'MOO!'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        )
    ]
)
def test_wwtp_jurisdictions(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'stormwater_input': 'yes'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'stormwater_input': 'YES'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'stormwater_input': 'no'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'stormwater_input': ''
            },
            does_not_raise(),
            None
        ),
        (
            {
                'stormwater_input': 'y'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'stormwater_input': 'n'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'stormwater_input': 'n/a'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        )
    ]
)
def test_stormwater_input(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'influent_equilibrated': 'yes'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'influent_equilibrated': 'YES'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'influent_equilibrated': 'no'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'influent_equilibrated': None
            },
            does_not_raise(),
            None
        ),
        (
            {
                'influent_equilibrated': 'y'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'influent_equilibrated': 'n'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'influent_equilibrated': 'n/a'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        )
    ]
)
def test_influent_equilibrated(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'sample_type': '24-hr flow-weighted composite'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sample_type': '12-hr manual composite'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sample_type': 'grab'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sample_type': 'GRAB'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sample_type': 'y'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'sample_type': 'n'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'sample_type': 'n/a'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        )
    ]
)
def test_sample_type(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'sample_matrix': 'raw wastewater'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sample_matrix': 'primary sludge'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sample_matrix': 'holding tank'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sample_matrix': 'HOLDING TANK'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sample_matrix': 'raw'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'sample_type': 'primary s'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'sample_type': 'holding'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        )
    ]
)
def test_sample_matrix(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'pretreatment': 'YES'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'pretreatment': 'no'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'pretreatment': ''
            },
            does_not_raise(),
            None
        ),
        (
            {
                'pretreatment': 'y'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'pretreatment': 'n'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'pretreatment': 'n/a'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        )
    ]
)
def test_pretreatment(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'pretreatment': 'yes',
                'pretreatment_specify': 'treated with chemicals'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'pretreatment': 'no',
                'pretreatment_specify': None
            },
            does_not_raise(),
            None
        ),
        (
            {
                'pretreatment': '',
                'pretreatment_specify': None
            },
            does_not_raise(),
            None
        ),
        (
            {
                'pretreatment': 'yes',
                'pretreatment_specify': None
            },
            pytest.raises(ValidationError),
            'If "pretreatment" is "yes", then specify the chemicals used.'
        )
    ]
)
def test_pretreatment_specify(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'solids_separation': 'filtration'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'solids_separation': 'centriguation'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'solids_separation': 'CENTRIGUATION'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'solids_separation': 'none'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'solids_separation': ''
            },
            does_not_raise(),
            None
        ),
        (
            {
                'solids_separation': 'filtered'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'solids_separation': 'centrig'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        )
    ]
)
def test_solids_separation(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'concentration_method': 'membrane filtration '
                'with acidification and mgcl2'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'concentration_method': 'membrane filtration with '
                'sample acidification, membrane recombined with '
                'separated solids'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'concentration_method': 'centricon ultrafiltration'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'concentration_method': 'none'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'concentration_method': 'ULTRACENTRIFUGATION'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'concentration_method': 'promega wastewater '
                'large volume tna capture kit'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'concentration_method': 'membrane filtration'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'concentration_method': 'centrifugation'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'concentration_method': ''
            },
            pytest.raises(ValidationError),
            'Field may not be null.'
        )
    ]
)
def test_concentration_method(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'extraction_method': 'qiagen allprep powerfecal dna/rna kit'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'extraction_method': 'qiagen rneasy kit'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'extraction_method': 'QIAGEN RNEASY KIT'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'extraction_method': 'promega manual tna kit'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'extraction_method': 'phenol chloroform'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'extraction_method': 'ht tna kit'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'extraction_method': 'powerviral dna/rna kit'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'extraction_method': 'none'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'extraction_method': ''
            },
            pytest.raises(ValidationError),
            'Field may not be null.'
        )
    ]
)
def test_extraction_method(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'ext_blank': 'yes'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'ext_blank': 'YES'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'ext_blank': 'no'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'ext_blank': ''
            },
            does_not_raise(),
            None
        ),
        (
            {
                'ext_blank': 'y'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'ext_blank': 'n'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'ext_blank': 'n/a'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        )
    ]
)
def test_ext_blank(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'rec_eff_percent': 52,
                'rec_eff_target_name': 'oc43',
                'rec_eff_spike_matrix': 'raw sample post pasteurization',
                'rec_eff_spike_conc': 0.324132
            },
            does_not_raise(),
            None
        ),
        (
            {
                'rec_eff_percent': 22,
                'rec_eff_target_name': 'OC43',
                'rec_eff_spike_matrix': 'RAW SAMPLE POST PASTEURIZATION',
                'rec_eff_spike_conc': 3.24132
            },
            does_not_raise(),
            None
        ),
        (
            {
                'rec_eff_percent': 63,
                'rec_eff_target_name': ''
            },
            pytest.raises(ValidationError),
            "If rec_eff_percent is not equal to -1, "
            "then 'rec_eff_target_name', "
            "'rec_eff_spike_matrix', "
            "and 'rec_eff_spike_conc' "
            "cannot be empty."
        ),
        (
            {
                'rec_eff_percent': 86,
                'rec_eff_target_name': 'phi6',
                'rec_eff_spike_matrix': ''
            },
            pytest.raises(ValidationError),
            "If rec_eff_percent is not equal to -1, "
            "then 'rec_eff_target_name', "
            "'rec_eff_spike_matrix', "
            "and 'rec_eff_spike_conc' "
            "cannot be empty."
        ),
        (
            {
                'rec_eff_percent': 57,
                'rec_eff_target_name': 'coliphage'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'rec_eff_percent': 63,
                'rec_eff_target_name': 'oc43',
                'rec_eff_spike_matrix': 'sample'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        )
    ]
)
def test_rec_eff(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'pcr_target': 'e_sarbeco'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'pcr_target': 'E_SARBECO'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'pcr_target': 'niid_2019-ncov_n'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'pcr_target': 'rdrp gene / ncov_ip4'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'pcr_target': 'n1 and n2 combined'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'pcr_target': 'N 1'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'pcr_target': 'sarbeco'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'pcr_target': ''
            },
            pytest.raises(ValidationError),
            'Field may not be null.'
        )
    ]
)
def test_pcr_target(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'pcr_type': 'qpcr'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'pcr_type': 'QPCR'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'pcr_type': 'fluidigm dpcr'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'pcr_type': 'raindance dpcr'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'pcr_type': 'pcr'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'pcr_type': 'fluidigm'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'pcr_type': ''
            },
            pytest.raises(ValidationError),
            'Field may not be null.'
        )
    ]
)
def test_pcr_type(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'hum_frac_mic_conc': 12.02,
                'hum_frac_mic_unit': 'copies/L wastewater',
                'hum_frac_target_mic': 'pepper mild mottle virus',
                'hum_frac_target_mic_ref': 'www.frac-conc-info.com'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'hum_frac_mic_conc': 0.9987,
                'hum_frac_mic_unit': 'copies/g wet sludge',
                'hum_frac_target_mic': 'crassphage'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'hum_frac_mic_conc': 0.9987,
                'hum_frac_mic_unit': 'COPIES/G WET SLUDGE',
                'hum_frac_target_mic': 'CRASSPHAGE'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'hum_frac_mic_conc': 112.700234,
                'hum_frac_mic_unit': 'log10 copies/g dry sludge',
                'hum_frac_target_mic': 'hf183'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'hum_frac_mic_conc': 22.021,
                'hum_frac_mic_unit': None  # test for this field
            },
            pytest.raises(ValidationError),
            'If hum_frac_mic_conc is not empty, then '
            'must provide hum_frac_mic_unit, '
            'hum_frac_target_mic, and '
            'hum_frac_target_mic_ref.'
        ),
        (
            {
                'hum_frac_mic_conc': 22.021,
                'hum_frac_mic_unit': 'log10 copies/g dry sludge',
                'hum_frac_target_mic': None  # test for this field
            },
            pytest.raises(ValidationError),
            'If hum_frac_mic_conc is not empty, then '
            'must provide hum_frac_mic_unit, '
            'hum_frac_target_mic, and '
            'hum_frac_target_mic_ref.'
        ),
        (
            {
                'hum_frac_mic_conc': 22.021,
                'hum_frac_mic_unit': 'log10 copies/g dry sludge',
                'hum_frac_target_mic': 'hf183',
                'hum_frac_target_mic_ref': None  # test for this field
            },
            pytest.raises(ValidationError),
            'If hum_frac_mic_conc is not empty, then '
            'must provide hum_frac_mic_unit, '
            'hum_frac_target_mic, and '
            'hum_frac_target_mic_ref.'
        ),
        (
            {
                'hum_frac_mic_conc': 22.021,
                'hum_frac_mic_unit': 'wastewater unit'  # test for this field
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'hum_frac_mic_conc': 112.700234,
                'hum_frac_mic_unit': 'log10 copies/g dry sludge',
                'hum_frac_target_mic': '183'  # test for this field
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
    ]
)
def test_hum_frac_mic_conc(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'hum_frac_chem_conc': 1.02,
                'hum_frac_chem_unit': 'micrograms/g dry sludge',
                'hum_frac_target_chem': 'caffeine',
                'hum_frac_target_chem_ref': 'chem-conc-info.com'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'hum_frac_chem_conc': 1.02,
                'hum_frac_chem_unit': 'MICROGRAMS/G DRY SLUDGE',
                'hum_frac_target_chem': 'CAFFEINE',
                'hum_frac_target_chem_ref': 'chem-conc-info.com'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'hum_frac_chem_conc': 33.87,
                'hum_frac_chem_unit': 'log10 micrograms/g wet sludge',
                'hum_frac_target_chem': 'sucralose',
                'hum_frac_target_chem_ref': 'chem conc resource'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'hum_frac_chem_conc': 22.021,
                'hum_frac_chem_unit': None  # test for this field
            },
            pytest.raises(ValidationError),
            'If hum_frac_chem_unit is not empty, '
            'then hum_frac_chem_unit, hum_frac_target_chem, '
            'and hum_frac_target_chem_ref cannot be null.'
        ),
        (
            {
                'hum_frac_chem_conc': 96.331,
                'hum_frac_target_chem': None  # test for this field
            },
            pytest.raises(ValidationError),
            'If hum_frac_chem_unit is not empty, '
            'then hum_frac_chem_unit, hum_frac_target_chem, '
            'and hum_frac_target_chem_ref cannot be null.'
        ),
        (
            {
                'hum_frac_chem_conc': 96.331,
                'hum_frac_target_chem_ref': None  # test for this field
            },
            pytest.raises(ValidationError),
            'If hum_frac_chem_unit is not empty, '
            'then hum_frac_chem_unit, hum_frac_target_chem, '
            'and hum_frac_target_chem_ref cannot be null.'
        ),
        (
            {
                'hum_frac_chem_conc': 22.021,
                'hum_frac_chem_unit': 'wastewater unit'  # test for this field
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'hum_frac_chem_conc': 33.87,
                'hum_frac_chem_unit': 'log10 micrograms/g wet sludge',
                'hum_frac_target_chem': 'sucra'  # test for this field
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
    ]
)
def test_hum_frac_chem_conc(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'other_norm_conc': 1.02,
                'other_norm_name': 'pepper mild mottle virus',
                'other_norm_unit': 'log10 micrograms/g dry sludge',
                'other_norm_ref': 'norm-conc-info.com'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'other_norm_conc': 33.07,
                'other_norm_name': 'caffeine',
                'other_norm_unit': 'micrograms/L wastewater',
                'other_norm_ref': 'norm conc resource'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'other_norm_conc': 33.07,
                'other_norm_name': 'CAFFEINE',
                'other_norm_unit': 'MICROGRAMS/L WASTEWATER',
                'other_norm_ref': 'norm conc resource'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'other_norm_conc': 22.021,
                'other_norm_unit': None  # test for this field
            },
            pytest.raises(ValidationError),
            'If other_norm_conc is not empty, then '
            'other_norm_name cannot be null.'
        ),
        (
            {
                'other_norm_conc': 96.331,
                'other_norm_name': None  # test for this field
            },
            pytest.raises(ValidationError),
            'If other_norm_conc is not empty, then '
            'other_norm_name cannot be null.'
        ),
        (
            {
                'other_norm_conc': 96.331,
                'other_norm_ref': None  # test for this field
            },
            pytest.raises(ValidationError),
            'If other_norm_conc is not empty, then '
            'other_norm_name cannot be null.'
        ),
        (
            {
                'other_norm_conc': 22.021,
                'other_norm_unit': 'wastewater unit'  # test for this field
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'other_norm_conc': 33.87,
                'other_norm_unit': 'micrograms/L wastewater',
                'other_norm_name': 'sucra'  # test for this field
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
    ]
)
def test_other_norm_conc(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'quant_stan_type': 'dna'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'quant_stan_type': 'rna'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'quant_stan_type': 'RNA'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'quant_stan_type': 'd'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'quant_stan_type': 'r'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        )
    ]
)
def test_quant_stan_type(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'inhibition_detect': 'yes',
                'inhibition_adjust': 'yes',
                'inhibition_method': 'our method we used'

            },
            does_not_raise(),
            None
        ),
        (
            {
                'inhibition_detect': 'no',
                'inhibition_adjust': 'no',
                'inhibition_method': 'sciencejournal.com'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'inhibition_detect': 'not tested',
                'inhibition_adjust': '',
                'inhibition_method': 'none'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'inhibition_detect': 'NOT TESTED',
                'inhibition_adjust': 'NO',
                'inhibition_method': 'none'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'inhibition_detect': 'yes',
                'inhibition_adjust': '',
                'inhibition_method': ''

            },
            pytest.raises(ValidationError),
            'Field may not be null.'
        ),
        (
            {
                'inhibition_detect': 'not tested',
                'inhibition_adjust': 'no',
                'inhibition_method': 'n/a'
            },
            pytest.raises(ValidationError),
            "'inhibition_method' must be 'none' "
            "if inhibition_detect == 'not tested'."
        ),
        (
            {
                'inhibition_detect': 'n',
                'inhibition_adjust': 'n'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'inhibition_detect': 'y',
                'inhibition_adjust': 'n'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'inhibition_detect': 'n/a',
                'inhibition_adjust': 'n/a'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        )
    ]
)
def test_inhibition_detect(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'num_no_target_control': '0'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'num_no_target_control': 'more than 3'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'num_no_target_control': 'MORE THAN 3'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'num_no_target_control': 'zero'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        ),
        (
            {
                'num_no_target_control': '> 3'
            },
            pytest.raises(ValidationError),
            'Must be one of:'
        )
    ]
)
def test_num_no_target_control(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'sample_collect_date': '2021-04-28'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sample_collect_date': get_future_date(0).strftime('%Y-%m-%d'),
                'test_result_date': get_future_date(24).strftime('%Y-%m-%d')
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sample_collect_date': get_future_date(48).strftime('%Y-%m-%d')
            },
            pytest.raises(ValidationError),
            "'sample_collect_date' cannot be after "
            "tomorrow's date."
        ),
        (
            {
                'sample_collect_date': '04/15/2021'
            },
            pytest.raises(ValidationError),
            'Not a valid date'
        )
    ]
)
def test_sample_collect_date(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'sample_collect_time': '23:04'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sample_collect_time': '04/15/2021'
            },
            pytest.raises(ValidationError),
            'Not a valid time'
        )
    ]
)
def test_sample_collect_time(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'time_zone': 'utc-08:00'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'time_zone': 'UTC-08:00'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'time_zone': None
            },
            does_not_raise(),
            None
        ),
        (
            {
                'time_zone': 'central'
            },
            pytest.raises(ValidationError),
            'String does not match expected pattern.'
        )
    ]
)
def test_time_zone(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'sample_matrix': 'post grit removal',
                'flow_rate': 41353200
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sample_matrix': 'primary sludge',
                'flow_rate': None
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sample_matrix': 'raw wastewater',
                'flow_rate': None
            },
            pytest.raises(ValidationError),
            "If 'sample_matrix' is liquid sampled from flowing source "
        )
    ]
)
def test_flow_rate(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'sample_id': 'RFDIE8AS-73619djfshf',
                'lab_id': 'fdsaier8873619djfshf'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sample_id': 'RFDIE8AS_73619djfshf',
                'lab_id': 'fdsaier-873619djfshf'
            },
            does_not_raise(),
            None
        ),
        (
            {
                # too many characters
                'sample_id': 'fdsaier8473619djfshf55fdafd',
            },
            pytest.raises(ValidationError),
            'String does not match expected pattern.'
        ),
        (
            {
                # illegal characters
                'lab_id': 'fdsa#$%8%73619djfshf',
            },
            pytest.raises(ValidationError),
            'String does not match expected pattern.'
        )
    ]
)
def test_sample_and_lab_id(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'test_result_date': '2021-04-28'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'test_result_date': get_future_date(24).strftime('%Y-%m-%d')
            },
            does_not_raise(),
            None
        ),
        (
            {
                'test_result_date': get_future_date(48).strftime('%Y-%m-%d')
            },
            pytest.raises(ValidationError),
            "'test_result_date' cannot be after "
            "tomorrow's date."
        ),
        (
            {
                'test_result_date': '2021-04-25',
                'sample_collect_date': '2021-04-29'
            },
            pytest.raises(ValidationError),
            "'test_result_date' cannot be "
            "before 'sample_collect_date'."
        ),
        (
            {
                'test_result_date': '04/15/2021'
            },
            pytest.raises(ValidationError),
            'Not a valid date'
        ),
        (
            {
                'test_result_date': ''
            },
            pytest.raises(ValidationError),
            'Field may not be null.'
        )
    ]
)
def test_result_date(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'sars_cov2_units': 'copies/L wastewater'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sars_cov2_units': 'COPIES/L WASTEWATER'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sars_cov2_units': 'copies wastewater'
            },
            pytest.raises(ValidationError),
            'Must be one of: '
        )
    ]
)
def test_sars_cov2_units(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'sars_cov2_std_error': None,
                'sars_cov2_cl_95_lo': 12,
                'sars_cov2_cl_95_up': 12
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sars_cov2_std_error': 0.09214,
                'sars_cov2_cl_95_lo': None,
                'sars_cov2_cl_95_up': None
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sars_cov2_std_error': 0.09214,
                'sars_cov2_cl_95_lo': 123984,
                'sars_cov2_cl_95_up': 4450494
            },
            pytest.raises(ValidationError),
            "If 'sars_cov2_std_error' has a non-empty value "
            "then 'sars_cov2_cl_95_lo' and "
            "'sars_cov2_cl_95_up' must be empty."
        )
    ]
)
def test_sars_cov2_err_validation(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'ntc_amplify': 'yes'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'ntc_amplify': 'NO'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'ntc_amplify': 'n'
            },
            pytest.raises(ValidationError),
            'Must be one of: '
        )
    ]
)
def test_ntc_amplify(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'sars_cov2_below_lod': 'yes'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sars_cov2_below_lod': 'NO'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'sars_cov2_below_lod': 'n'
            },
            pytest.raises(ValidationError),
            'Must be one of: '
        )
    ]
)
def test_sars_cov2_below_lod(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)


@pytest.mark.parametrize(
    'input,expect,error',
    [
        (
            {
                'quality_flag': 'yes'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'quality_flag': 'NO'
            },
            does_not_raise(),
            None
        ),
        (
            {
                'quality_flag': 'n'
            },
            pytest.raises(ValidationError),
            'Must be one of: '
        )
    ]
)
def test_quality_flag(schema, valid_data, input, expect, error):
    data = update_data(input, valid_data)

    with expect as e:
        schema.load(data)

    if e:
        assert error in str(e.value)
