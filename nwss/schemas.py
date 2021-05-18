import re
from marshmallow import Schema, fields, \
    validate, ValidationError, validates_schema, validates
from marshmallow.decorators import pre_load

from nwss import value_sets, fields as nwss_fields
from nwss.utils import get_future_date


class CaseInsensitiveOneOf(validate.OneOf):
    _jsonschema_base_validator_class = validate.OneOf

    def __call__(self, value) -> str:
        try:
            if not any(value.casefold() == v.casefold() for v in self.choices):
                raise ValidationError(self._format_error(value))
        except TypeError as error:
            raise ValidationError(self._format_error(value)) from error

        return value


class CollectionSite():
    reporting_jurisdiction = fields.String(
        required=True,
        validate=CaseInsensitiveOneOf(value_sets.reporting_jurisdiction)
    )

    county_names = nwss_fields.ListString(missing=None)
    other_jurisdiction = nwss_fields.ListString(missing=None)

    @validates_schema
    def validate_county_jurisdiction(self, data, **kwargs):
        if not data['county_names'] and not data['other_jurisdiction']:
            raise ValidationError('Either county_names or other_jurisdiction '
                                  'must have a value.')

    zipcode = fields.String(
        required=True,
        validate=validate.Length(min=5, max=5)
    )

    population_served = fields.Int(
        required=True,
        validate=validate.Range(min=0)
    )

    sewage_travel_time = fields.Float(
        validate=validate.Range(min=0),
        allow_none=True,
        metadata={'units': 'Time in hours.'}
    )

    sample_location = fields.String(
        required=True,
        validate=CaseInsensitiveOneOf(value_sets.sample_location)
    )

    sample_location_specify = fields.Str(
        validate=validate.Length(min=0, max=40),
        allow_none=True
    )

    @validates_schema
    def validate_sample_location(self, data, **kwargs):
        if data['sample_location'] == 'upstream' \
          and not data.get('sample_location_specify', None):
            raise ValidationError('An "upstream" sample_location must have '
                                  'a value for sample_location_specify.')

    institution_type = fields.String(
        required=True,
        validate=CaseInsensitiveOneOf(value_sets.institution_type)
    )


class WWTP():
    epaid = fields.String(
        allow_none=True,
        validate=validate.Regexp('^([a-zA-Z]{2})(\\d{7})$')
    )

    wwtp_name = fields.String(
        required=True,
        validate=validate.Length(max=40)
    )

    wwtp_jurisdiction = fields.String(
        required=True,
        validate=CaseInsensitiveOneOf(value_sets.wwtp_jurisdictions)
    )

    capacity_mgd = fields.Float(
        required=True,
        validate=validate.Range(min=0),
        metadata={'units': 'Million gallons per day (MGD)'}
    )

    industrial_input = fields.Float(
        allow_none=True,
        validate=validate.Range(min=0, max=100),
        metadata={'units': 'Percent'}
    )

    stormwater_input = fields.String(
        allow_none=True,
        validate=CaseInsensitiveOneOf(value_sets.yes_no_empty)
    )

    influent_equilibrated = fields.String(
        allow_none=True,
        validate=CaseInsensitiveOneOf(value_sets.yes_no_empty)
    )


class CollectionMethod():
    sample_type = fields.String(
        required=True,
        validate=CaseInsensitiveOneOf(value_sets.sample_type)
    )

    composite_freq = fields.Float(
        allow_none=True,
        validate=validate.Range(min=0),
        metadata={
                'units': 'Flow-weighted composite: number per million gallons;'
                         ' Time-weighted or manual composite: number per hour'
            }
    )

    sample_matrix = fields.String(
        required=True,
        validate=CaseInsensitiveOneOf(value_sets.sample_matrix)
    )

    collection_storage_time = fields.Float(
        allow_none=True,
        validate=validate.Range(min=0),
        metadata={'units': 'Hours'}
    )

    collection_storage_temp = fields.Float(
        allow_none=True,
        metadata={'units': 'Celsius'}
    )

    pretreatment = fields.String(
        allow_none=True,
        validate=CaseInsensitiveOneOf(value_sets.yes_no_empty)
    )

    pretreatment_specify = fields.String(
        allow_none=True,
    )

    @validates_schema
    def validate_pretreatment(self, data, **kwargs):
        if data['pretreatment'] == 'yes' \
          and not data.get('pretreatment_specify'):
            raise ValidationError(
                'If "pretreatment" is "yes", then specify '
                'the chemicals used.'
            )


class ProcessingMethod():
    solids_separation = fields.String(
        allow_none=True,
        validate=CaseInsensitiveOneOf(value_sets.solids_separation)
    )

    concentration_method = fields.String(
        required=True,
        validate=CaseInsensitiveOneOf(value_sets.concentration_method)
    )

    extraction_method = fields.String(
        required=True,
        validate=CaseInsensitiveOneOf(value_sets.extraction_method)
    )

    pre_conc_storage_time = fields.Float(
        allow_none=True,
        validate=validate.Range(min=0),
        metadata={'units': 'Hours'}
    )

    pre_conc_storage_temp = fields.Float(
        allow_none=True,
        metadata={'units': 'Celsius'}
    )

    pre_ext_storage_time = fields.Float(
        allow_none=True,
        validate=validate.Range(min=0),
        metadata={'units': 'Hours'}
    )

    pre_ext_storage_temp = fields.Float(
        allow_none=True,
        metadata={'units': 'Celsius'}
    )

    tot_conc_vol = fields.Float(
        allow_none=True,
        validate=validate.Range(min=0),
        metadata={'units': 'mL'}
    )

    ext_blank = fields.String(
        allow_none=True,
        validate=CaseInsensitiveOneOf(value_sets.yes_no_empty)
    )

    rec_eff_percent = fields.Float(
        required=True,
        validate=validate.Range(min=-1),
        metadata={'units': 'percent'}
    )

    rec_eff_target_name = fields.String(
        allow_none=True,
        validate=CaseInsensitiveOneOf(value_sets.rec_eff_target_name)
    )

    rec_eff_spike_matrix = fields.String(
        allow_none=True,
        validate=CaseInsensitiveOneOf(value_sets.rec_eff_spike_matrix)
    )

    rec_eff_spike_conc = fields.Float(
        allow_none=True,
        metadata={'units': 'log10 copies/mL'}
    )

    @validates_schema
    def validate_rec_eff(self, data, **kwargs):
        dependent = [
            'rec_eff_target_name',
            'rec_eff_spike_matrix',
            'rec_eff_spike_conc'
        ]

        if data['rec_eff_percent'] != -1 \
           and not all(data.get(k) for k in dependent):
            raise ValidationError(
                "If rec_eff_percent is not equal to -1, "
                "then 'rec_eff_target_name', "
                "'rec_eff_spike_matrix', "
                "and 'rec_eff_spike_conc' "
                "cannot be empty."
            )

    pasteurized = fields.String(
        allow_none=True,
        validate=CaseInsensitiveOneOf(value_sets.yes_no_empty)
    )


class QuantificationMethod():
    pcr_target = fields.String(
        required=True,
        validate=CaseInsensitiveOneOf(value_sets.pcr_target)
    )

    pcr_target_ref = fields.String(
        required=True
    )

    pcr_type = fields.String(
        required=True,
        validate=CaseInsensitiveOneOf(value_sets.pcr_type)
    )

    lod_ref = fields.String(
        required=True
    )

    hum_frac_mic_conc = fields.Float(
        allow_none=True,
        metadata={'units': "specified in 'hum_frac_mic_unit'"}
    )

    hum_frac_mic_unit = fields.String(
        allow_none=True,
        validate=CaseInsensitiveOneOf(value_sets.mic_units)
    )

    hum_frac_target_mic = fields.String(
        allow_none=True,
        validate=CaseInsensitiveOneOf(value_sets.hum_frac_target_mic)
    )

    hum_frac_target_mic_ref = fields.String(
        allow_none=True
    )

    @validates_schema
    def validate_hum_frac_mic_conc(self, data, **kwargs):
        """
        If hum_frac_mic_conc is not empty, then
         validate that the dependent fields
         are not empty.
        """
        dependent = [
            'hum_frac_mic_unit',
            'hum_frac_target_mic',
            'hum_frac_target_mic_ref'
        ]

        if data.get('hum_frac_mic_conc') \
           and not all(data.get(key) for key in dependent):
            raise ValidationError(
                'If hum_frac_mic_conc is not empty, then '
                'must provide hum_frac_mic_unit, '
                'hum_frac_target_mic, and '
                'hum_frac_target_mic_ref.'
            )

    hum_frac_chem_conc = fields.Float(
        allow_none=True,
        metadata={'units': "specified in 'hum_frac_chem_unit'."}
    )

    hum_frac_chem_unit = fields.String(
        allow_none=True,
        validate=CaseInsensitiveOneOf(value_sets.chem_units)
    )

    hum_frac_target_chem = fields.String(
        allow_none=True,
        validate=CaseInsensitiveOneOf(value_sets.hum_frac_target_chem)
    )

    hum_frac_target_chem_ref = fields.String(
        allow_none=True
    )

    @validates_schema
    def validate_hum_frac_chem_conc(self, data, **kwargs):
        """
        If hum_frac_chem_conc is not empty, then
         validate that the dependent fields
         are not empty.
        """
        dependent = [
            'hum_frac_chem_unit',
            'hum_frac_target_chem',
            'hum_frac_target_chem_ref'
        ]

        if data.get('hum_frac_chem_conc') \
           and not all(data.get(key) for key in dependent):
            raise ValidationError(
                'If hum_frac_chem_unit is not empty, '
                'then hum_frac_chem_unit, hum_frac_target_chem, '
                'and hum_frac_target_chem_ref cannot be null.'
            )

    other_norm_conc = fields.Float(
        allow_none=True
    )

    other_norm_name = fields.String(
        allow_none=True,
        validate=CaseInsensitiveOneOf(value_sets.other_norm_name)
    )

    other_norm_unit = fields.String(
        allow_none=True,
        validate=CaseInsensitiveOneOf(value_sets.mic_chem_units)
    )

    other_norm_ref = fields.String(
        allow_none=True
    )

    @validates_schema
    def validate_other_norm_conc(self, data, **kwargs):
        """
        If other_norm_conc is not empty, then
         validate that the dependent fields
         are not empty.
        """
        dependent = [
            'other_norm_name',
            'other_norm_unit',
            'other_norm_ref'
        ]

        if data.get('other_norm_conc') \
           and not all(data.get(key) for key in dependent):
            raise ValidationError(
                    'If other_norm_conc is not empty, then '
                    'other_norm_name cannot be null.'
            )

    quant_stan_type = fields.String(
        required=True,
        validate=CaseInsensitiveOneOf(value_sets.quant_stan_type)
    )

    stan_ref = fields.String(
        required=True
    )

    inhibition_detect = fields.String(
        required=True,
        validate=CaseInsensitiveOneOf(value_sets.yes_no_not_tested)
    )

    inhibition_adjust = fields.String(
        allow_none=True,
        validate=CaseInsensitiveOneOf(value_sets.yes_no_empty)
    )

    inhibition_method = fields.String(
        required=True
    )

    @validates_schema
    def validate_inhibition_detect(self, data, **kwargs):
        if data['inhibition_detect'] == 'yes' \
           and not data['inhibition_adjust']:
            raise ValidationError(
                "If 'inhibition_detect' is yes, "
                "then 'inhibition_adjust' must have "
                "a non-empty value."
            )

        if data['inhibition_detect'] == 'not tested' \
           and data['inhibition_method'] != 'none':
            raise ValidationError(
                "'inhibition_method' must be 'none' "
                "if inhibition_detect == 'not tested'."
            )

    num_no_target_control = fields.String(
        required=True,
        validate=CaseInsensitiveOneOf(value_sets.num_no_target_control)
    )


class Sample():
    sample_collect_date = fields.Date(
        required=True
    )

    @validates('sample_collect_date')
    def validate_sample_collect_date(self, value):
        tomorrow = get_future_date(24)

        if value > tomorrow:
            raise ValidationError(
                "'sample_collect_date' cannot be after "
                "tomorrow's date."
            )

    sample_collect_time = fields.Time(
        required=True
    )

    time_zone = fields.String(
        allow_none=True,
        validate=validate.Regexp('utc-(\\d{2}):(\\d{2})', re.IGNORECASE)
    )

    flow_rate = fields.Float(
        allow_none=True,
        validate=validate.Range(min=0),
        metadata={'units': 'Million gallons per day (MGD)'}
    )

    @validates_schema
    def validate_flow_rate(self, data, **kwargs):
        sample_matrix_required = [
            'raw wastewater',
            'post grit removal',
            'primary effluent',
            'secondary effluent'
        ]

        if data['sample_matrix'] in sample_matrix_required \
           and not data['flow_rate']:
            required = ','.join(sample_matrix_required)
            raise ValidationError(
                "If 'sample_matrix' is liquid sampled from flowing source "
                f"({required}), then 'flow_rate' must have a non-empty value."
            )

    ph = fields.Float(
        allow_none=True,
        metadata={'units': 'pH units'}
    )

    conductivity = fields.Float(
        allow_none=True,
        validate=validate.Range(min=0),
        metadata={'units': 'microsiemens/cm'}
    )

    tss = fields.Float(
        allow_none=True,
        validate=validate.Range(min=0),
        metadata={'units': 'mg/L'}
    )

    collection_water_temp = fields.Float(
        allow_none=True,
        validate=validate.Range(min=0),
        metadata={'units': 'Celsius'}
    )

    equiv_sewage_amt = fields.Float(
        allow_none=True,
        validate=validate.Range(min=0),
        metadata={'units': 'mL wastewater or g sludge'}
    )

    sample_id = fields.String(
        required=True,
        validate=validate.Regexp('^[a-zA-Z0-9-_]{1,20}$')
    )

    lab_id = fields.String(
        required=True,
        validate=validate.Regexp('^[a-zA-Z0-9-_]{1,20}$')
    )


class QuantificationResults():
    test_result_date = fields.Date(
        required=True
    )

    @validates_schema
    def validate_test_result_date(self, data, **kwargs):
        tomorrow = get_future_date(24)

        result_date = data['test_result_date']

        if result_date > tomorrow:
            raise ValidationError(
                "'test_result_date' cannot be after "
                "tomorrow's date."
            )

        if data['sample_collect_date'] > result_date:
            raise ValidationError(
                "'test_result_date' cannot be "
                "before 'sample_collect_date'."
            )

    sars_cov2_units = fields.String(
        required=True,
        validate=CaseInsensitiveOneOf(value_sets.mic_chem_units)
    )

    sars_cov2_avg_conc = fields.Float(
        required=True,
        metadata={'units': 'specified in sars_cov2_units'}
    )

    sars_cov2_std_error = fields.Float(
        allow_none=True,
        validate=validate.Range(min=-1),
        metadata={'units': 'specified in sars_cov2_units'}
    )

    sars_cov2_cl_95_lo = fields.Float(
        allow_none=True,
        metadata={'units': 'specified in sars_cov2_units'}
    )

    sars_cov2_cl_95_up = fields.Float(
        allow_none=True,
        metadata={'units': 'specified in sars_cov2_units'}
    )

    @validates_schema
    def validate_sars_cov2(self, data, **kwargs):
        fields = [
            'sars_cov2_std_error',
            'sars_cov2_cl_95_lo',
            'sars_cov2_cl_95_up'
        ]

        if all(data.get(field) for field in fields):
            raise ValidationError(
                   "If 'sars_cov2_std_error' has a non-empty value then "
                   "'sars_cov2_cl_95_lo' and 'sars_cov2_cl_95_up' "
                   "must be empty."
               )

    ntc_amplify = fields.String(
        required=True,
        validate=CaseInsensitiveOneOf(value_sets.yes_no)
    )

    sars_cov2_below_lod = fields.String(
        required=True,
        validate=CaseInsensitiveOneOf(value_sets.yes_no)
    )

    lod_sewage = fields.Float(
        required=True,
        metadata={'units': 'specified in sars_cov2_units'}
    )

    quality_flag = fields.String(
        allow_none=True,
        validate=CaseInsensitiveOneOf(value_sets.yes_no_empty)
    )


class WaterSampleSchema(
        CollectionSite,
        WWTP,
        CollectionMethod,
        ProcessingMethod,
        QuantificationMethod,
        Sample,
        QuantificationResults,
        Schema):

    class Meta:
        additional_properties = True

    @pre_load
    def cast_to_none(self, raw_data, **kwargs):
        """Cast empty strings to None to provide for the use of
        the allow_none flag by optional numeric fields.
        """
        return {k: v if v != '' else None for k, v in raw_data.items()}
