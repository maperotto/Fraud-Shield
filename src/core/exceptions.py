class FraudShieldException(Exception):
    pass


class ModelNotTrainedException(FraudShieldException):
    pass


class InvalidTransactionException(FraudShieldException):
    pass


class DataNotFoundException(FraudShieldException):
    pass
