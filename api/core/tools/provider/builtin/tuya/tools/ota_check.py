from typing import Any, Optional, Union

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool


class OtaDiagnoseInput(BaseModel):
    dev_id: str = Field(..., description="device id.")


class OtaCheckApiWrapper(BaseModel):

    def run(self, dev_id: str) -> str:
        """Run Wikipedia search and get page summaries."""
        return '设备已经是最新版本'


class OtaCheckDiagnoseRun(BaseTool):
    name = "OTA diagnose"
    description = (
        "A wrapper around OTA diagnose tool. "
        "Useful for when you need to diagnose device ota issues "
        "Input should be a device id."
    )
    api_wrapper: OtaCheckApiWrapper

    def _run(
            self,
            dev_id: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the Wikipedia tool."""
        return self.api_wrapper.run(dev_id)


class OtaCheckDiagnoseTool(BuiltinTool):
    def _invoke(self,
                user_id: str,
                tool_paramters: dict[str, Any],
                ) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
            invoke tools
        """
        dev_id = tool_paramters.get('dev', '')
        if not dev_id:
            return self.create_text_message('Please input device id')

        tool = OtaCheckDiagnoseRun(
            name="OTA check diagnose",
            api_wrapper=OtaCheckApiWrapper(doc_content_chars_max=4000),
            args_schema=OtaDiagnoseInput
        )

        result = tool.run(tool_input={
            'dev_id': dev_id,
        })

        return self.create_text_message(self.summary(user_id=user_id, content=result))
