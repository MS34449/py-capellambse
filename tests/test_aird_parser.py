# Copyright 2021 DB Netz AG
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import pathlib
import sys

import pytest

from capellambse import MelodyModel, aird, loader


class TestAIRDBasicFunctionality:
    test_model = (
        pathlib.Path(__file__).parent / "data" / "parser" / "TestItems.aird"
    )
    test_diagram = "[LAB] Logical System"
    test_json = test_model.with_suffix(".json")
    test_repr = test_model.with_suffix(".repr.txt")
    test_txt = test_model.with_suffix(".txt")

    @pytest.fixture
    def model(self):
        return loader.MelodyLoader(self.test_model)

    @pytest.fixture
    def diagram_under_test(self, model):
        descriptor = next(aird.enumerate_diagrams(model), None)
        assert descriptor is not None
        yield aird.parse_diagram(model, descriptor)

    def test_parsing_all_diagrams_does_not_raise_exceptions(
        self, model, caplog
    ):
        del caplog
        i = 0
        for i, _ in enumerate(aird.parse_diagrams(model), start=1):
            pass
        assert i == 1

    @pytest.mark.xfail(
        sys.platform not in {"win32", "cygwin"},
        reason="Expected rendering inaccuracies on non-Windows platforms",
    )
    @pytest.mark.skip(reason="Currently broken")
    def test_json_output_matches_expected_output(
        self, diagram_under_test, caplog
    ):
        del caplog
        expected = self.test_json.read_text().strip()
        actual = aird.DiagramJSONEncoder(indent=4).encode(diagram_under_test)
        assert actual == expected

    @pytest.mark.xfail(
        sys.platform not in {"win32", "cygwin"},
        reason="Expected rendering inaccuracies on non-Windows platforms",
    )
    @pytest.mark.skip(reason="Currently broken")
    def test_plain_text_representation_matches_expected_output(
        self, diagram_under_test, caplog
    ):
        del caplog
        expected = self.test_txt.read_text()
        actual = str(diagram_under_test)
        assert actual + "\n" == expected

    @pytest.mark.xfail(
        sys.platform not in {"win32", "cygwin"},
        reason="Expected rendering inaccuracies on non-Windows platforms",
    )
    @pytest.mark.skip(reason="Currently broken")
    def test_python_code_representation_matches_expected_output(
        self, diagram_under_test, caplog
    ):
        del caplog
        expected = self.test_repr.read_text().strip()
        actual = repr(diagram_under_test)
        assert actual == expected


def test_airdparser_msm_produces_valid_json_without_error(model: MelodyModel):
    diag_name = "[MSM] States of Functional Human Being"
    all_diagrams = aird.enumerate_diagrams(model._loader)
    descriptor = next(i for i in all_diagrams if i.name == diag_name)
    diagram = aird.parse_diagram(model._loader, descriptor)

    generated_json = aird.DiagramJSONEncoder(indent=4).encode(diagram)
    json.loads(generated_json)
