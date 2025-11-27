import pytest
from app.utils.exceptions import AgentException

class TestAgentExceptionSignature:
    """
    Tests pour valider la signature correcte de AgentException.
    Le bug précédent était l'utilisation de 3 arguments positionnels.
    La signature correcte est : AgentException(message, **kwargs)
    """

    def test_agent_exception_with_message_only(self):
        """Vérifie l'instanciation avec uniquement un message."""
        exc = AgentException("Something went wrong")
        assert str(exc) == "Something went wrong"
        assert exc.message == "Something went wrong"
        assert exc.error_code == "GENESIS_AGENT_ERROR"  # Default

    def test_agent_exception_with_all_kwargs(self):
        """Vérifie l'instanciation avec message et kwargs (error_code, details)."""
        details = {"foo": "bar"}
        exc = AgentException(
            message="Custom error",
            error_code="CUSTOM_CODE",
            details=details,
            status_code=400
        )
        assert exc.message == "Custom error"
        assert exc.error_code == "CUSTOM_CODE"
        assert exc.details == details
        assert exc.status_code == 400

    def test_agent_exception_default_values(self):
        """Vérifie les valeurs par défaut."""
        exc = AgentException()
        assert exc.message == "Agent error"
        assert exc.status_code == 500

    def test_agent_exception_no_positional_args_error(self):
        """
        Vérifie que passer trop d'arguments positionnels lève bien une TypeError.
        C'est ce test qui aurait dû échouer avec l'ancien code.
        """
        with pytest.raises(TypeError) as excinfo:
            # Simulation de l'appel incorrect qui causait le bug
            # AgentException("CODE", "Message", details=...)
            AgentException("ERROR_CODE", "Message", details={})
        
        assert "takes from 1 to 2 positional arguments but 3 were given" in str(excinfo.value)
