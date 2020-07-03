"""
Re-implementation of this collector using the param_injector, range_inference
and entry_probing modules
"""

import requests
import logging
import os

from range_inference import RangeInference
from param_injector import ParamInjector
from entry_probing import EntryProbing, GETProbingRequest,\
                          HTTPStatusProbingResponse, TextMatchProbingResponse

base = "http://geoobras.tce.mg.gov.br/cidadao/Obras/ObrasPaginaInteiraDetalhes.aspx?IDOBRA={}"
not_found = "possivel localizar a obra"

probe = EntryProbing(GETProbingRequest(base))
probe.add_response_handler(HTTPStatusProbingResponse(200))\
     .add_response_handler(TextMatchProbingResponse(not_found, opposite=True))

print("Calculating upper bound")
upper_bound = RangeInference.filter_numeric_range(0, 50000, probe)
print("UB: {}".format(upper_bound))

for i in ParamInjector.generate_num_sequence(0, upper_bound, 1, False):
    found = probe.check_entry(i)
    if found:
        response = probe.response # requests.get(base.format(i))
        content = response.text
        folder = "obras" + str(int(i)%100)
        if not os.path.exists("obras_tce/" + folder):
            os.makedirs("obras_tce/" + folder)
        with open("obras_tce/" + folder + "/obra_id" + str(i), "w") as f:
            f.write(content)
