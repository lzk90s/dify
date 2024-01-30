from core.tools.errors import ToolProviderCredentialValidationError
from core.tools.provider.builtin.tuya.tools.ota_check import OtaCheckDiagnoseTool
from core.tools.provider.builtin_tool_provider import BuiltinToolProviderController


class WikiPediaProvider(BuiltinToolProviderController):
    def _validate_credentials(self, credentials: dict) -> None:
        try:
            OtaCheckDiagnoseTool().fork_tool_runtime(
                meta={
                    "credentials": credentials,
                }
            ).invoke(
                user_id='',
                tool_paramters={
                    "query": "misaka mikoto",
                },
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
