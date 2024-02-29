from typing import Any, Optional, Union

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.provider.builtin.tuya.tools.dev_factory import DeviceFactory, DeviceNotExistError
from core.tools.tool.builtin_tool import BuiltinTool


class OtaDiagnoseInput(BaseModel):
    dev_id: str = Field(..., description="device id.")


class OtaFailDiagnoseRun(BaseTool):
    name = "OTA fail diagnose"
    description = (
        "A wrapper around OTA diagnose tool. "
        "Useful for when you need to diagnose device ota issues "
        "Input should be a device id."
    )

    def _run(
            self,
            dev_id: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            return 'reason:' + DeviceFactory.find_dev_by_id(dev_id).diagnose('OTA_FAIL')
        except DeviceNotExistError as e:
            return 'device not exist!'


class OtaFailDiagnoseTool(BuiltinTool):
    def _invoke(self,
                user_id: str,
                tool_parameters: dict[str, Any],
                ) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
            invoke tools
        """
        dev_id = tool_parameters.get('dev', '')
        if not dev_id:
            return self.create_text_message('Please input device id')

        tool = OtaFailDiagnoseRun(
            name="OTA fail diagnose",
            args_schema=OtaDiagnoseInput
        )

        result = tool.run(tool_input={
            'dev_id': dev_id,
        })

        return self.create_text_message(self.summary(user_id=user_id, content=result))
