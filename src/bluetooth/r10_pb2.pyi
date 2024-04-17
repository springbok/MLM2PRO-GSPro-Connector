from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WrapperProto(_message.Message):
    __slots__ = ("event", "service")
    EVENT_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    event: EventSharing
    service: LaunchMonitorService
    def __init__(self, event: _Optional[_Union[EventSharing, _Mapping]] = ..., service: _Optional[_Union[LaunchMonitorService, _Mapping]] = ...) -> None: ...

class LaunchMonitorService(_message.Message):
    __slots__ = ("status_request", "status_response", "wake_up_request", "wake_up_response", "tilt_request", "tilt_response", "start_tilt_cal_request", "start_tilt_cal_response", "reset_tilt_cal_request", "reset_tilt_cal_response", "shot_config_request", "shot_config_response")
    STATUS_REQUEST_FIELD_NUMBER: _ClassVar[int]
    STATUS_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    WAKE_UP_REQUEST_FIELD_NUMBER: _ClassVar[int]
    WAKE_UP_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    TILT_REQUEST_FIELD_NUMBER: _ClassVar[int]
    TILT_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    START_TILT_CAL_REQUEST_FIELD_NUMBER: _ClassVar[int]
    START_TILT_CAL_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    RESET_TILT_CAL_REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESET_TILT_CAL_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    SHOT_CONFIG_REQUEST_FIELD_NUMBER: _ClassVar[int]
    SHOT_CONFIG_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    status_request: StatusRequest
    status_response: StatusResponse
    wake_up_request: WakeUpRequest
    wake_up_response: WakeUpResponse
    tilt_request: TiltRequest
    tilt_response: TiltResponse
    start_tilt_cal_request: StartTiltCalibrationRequest
    start_tilt_cal_response: StartTiltCalibrationResponse
    reset_tilt_cal_request: ResetTiltCalibrationRequest
    reset_tilt_cal_response: ResetTiltCalibrationResponse
    shot_config_request: ShotConfigRequest
    shot_config_response: ShotConfigResponse
    def __init__(self, status_request: _Optional[_Union[StatusRequest, _Mapping]] = ..., status_response: _Optional[_Union[StatusResponse, _Mapping]] = ..., wake_up_request: _Optional[_Union[WakeUpRequest, _Mapping]] = ..., wake_up_response: _Optional[_Union[WakeUpResponse, _Mapping]] = ..., tilt_request: _Optional[_Union[TiltRequest, _Mapping]] = ..., tilt_response: _Optional[_Union[TiltResponse, _Mapping]] = ..., start_tilt_cal_request: _Optional[_Union[StartTiltCalibrationRequest, _Mapping]] = ..., start_tilt_cal_response: _Optional[_Union[StartTiltCalibrationResponse, _Mapping]] = ..., reset_tilt_cal_request: _Optional[_Union[ResetTiltCalibrationRequest, _Mapping]] = ..., reset_tilt_cal_response: _Optional[_Union[ResetTiltCalibrationResponse, _Mapping]] = ..., shot_config_request: _Optional[_Union[ShotConfigRequest, _Mapping]] = ..., shot_config_response: _Optional[_Union[ShotConfigResponse, _Mapping]] = ...) -> None: ...

class StatusRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StatusResponse(_message.Message):
    __slots__ = ("state",)
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: State
    def __init__(self, state: _Optional[_Union[State, _Mapping]] = ...) -> None: ...

class WakeUpRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WakeUpResponse(_message.Message):
    __slots__ = ("status",)
    class ResponseStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUCCESS: _ClassVar[WakeUpResponse.ResponseStatus]
        ALREADY_AWAKE: _ClassVar[WakeUpResponse.ResponseStatus]
        UNKNOWN_ERROR: _ClassVar[WakeUpResponse.ResponseStatus]
    SUCCESS: WakeUpResponse.ResponseStatus
    ALREADY_AWAKE: WakeUpResponse.ResponseStatus
    UNKNOWN_ERROR: WakeUpResponse.ResponseStatus
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: WakeUpResponse.ResponseStatus
    def __init__(self, status: _Optional[_Union[WakeUpResponse.ResponseStatus, str]] = ...) -> None: ...

class TiltRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TiltResponse(_message.Message):
    __slots__ = ("tilt",)
    TILT_FIELD_NUMBER: _ClassVar[int]
    tilt: Tilt
    def __init__(self, tilt: _Optional[_Union[Tilt, _Mapping]] = ...) -> None: ...

class StartTiltCalibrationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StartTiltCalibrationResponse(_message.Message):
    __slots__ = ("status",)
    class CalibrationStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STARTED: _ClassVar[StartTiltCalibrationResponse.CalibrationStatus]
        IN_PROGRESS: _ClassVar[StartTiltCalibrationResponse.CalibrationStatus]
        ERROR: _ClassVar[StartTiltCalibrationResponse.CalibrationStatus]
    STARTED: StartTiltCalibrationResponse.CalibrationStatus
    IN_PROGRESS: StartTiltCalibrationResponse.CalibrationStatus
    ERROR: StartTiltCalibrationResponse.CalibrationStatus
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: StartTiltCalibrationResponse.CalibrationStatus
    def __init__(self, status: _Optional[_Union[StartTiltCalibrationResponse.CalibrationStatus, str]] = ...) -> None: ...

class ResetTiltCalibrationRequest(_message.Message):
    __slots__ = ("should_reset",)
    SHOULD_RESET_FIELD_NUMBER: _ClassVar[int]
    should_reset: bool
    def __init__(self, should_reset: bool = ...) -> None: ...

class ResetTiltCalibrationResponse(_message.Message):
    __slots__ = ("status",)
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[ResetTiltCalibrationResponse.Status]
        CAN_RESET: _ClassVar[ResetTiltCalibrationResponse.Status]
        ALREADY_RESET: _ClassVar[ResetTiltCalibrationResponse.Status]
        RESET_SUCCESSFUL: _ClassVar[ResetTiltCalibrationResponse.Status]
        CANNOT_RESET: _ClassVar[ResetTiltCalibrationResponse.Status]
    UNKNOWN: ResetTiltCalibrationResponse.Status
    CAN_RESET: ResetTiltCalibrationResponse.Status
    ALREADY_RESET: ResetTiltCalibrationResponse.Status
    RESET_SUCCESSFUL: ResetTiltCalibrationResponse.Status
    CANNOT_RESET: ResetTiltCalibrationResponse.Status
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: ResetTiltCalibrationResponse.Status
    def __init__(self, status: _Optional[_Union[ResetTiltCalibrationResponse.Status, str]] = ...) -> None: ...

class ShotConfigRequest(_message.Message):
    __slots__ = ("temperature", "humidity", "altitude", "air_density", "tee_range")
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    HUMIDITY_FIELD_NUMBER: _ClassVar[int]
    ALTITUDE_FIELD_NUMBER: _ClassVar[int]
    AIR_DENSITY_FIELD_NUMBER: _ClassVar[int]
    TEE_RANGE_FIELD_NUMBER: _ClassVar[int]
    temperature: float
    humidity: float
    altitude: float
    air_density: float
    tee_range: float
    def __init__(self, temperature: _Optional[float] = ..., humidity: _Optional[float] = ..., altitude: _Optional[float] = ..., air_density: _Optional[float] = ..., tee_range: _Optional[float] = ...) -> None: ...

class ShotConfigResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class EventSharing(_message.Message):
    __slots__ = ("subscribe_request", "subscribe_respose", "notification", "support_request", "support_response")
    SUBSCRIBE_REQUEST_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBE_RESPOSE_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATION_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_REQUEST_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    subscribe_request: SubscribeRequest
    subscribe_respose: SubscribeResponse
    notification: AlertNotification
    support_request: AlertSupportRequest
    support_response: AlertSupportResponse
    def __init__(self, subscribe_request: _Optional[_Union[SubscribeRequest, _Mapping]] = ..., subscribe_respose: _Optional[_Union[SubscribeResponse, _Mapping]] = ..., notification: _Optional[_Union[AlertNotification, _Mapping]] = ..., support_request: _Optional[_Union[AlertSupportRequest, _Mapping]] = ..., support_response: _Optional[_Union[AlertSupportResponse, _Mapping]] = ...) -> None: ...

class SubscribeRequest(_message.Message):
    __slots__ = ("alerts",)
    ALERTS_FIELD_NUMBER: _ClassVar[int]
    alerts: _containers.RepeatedCompositeFieldContainer[AlertMessage]
    def __init__(self, alerts: _Optional[_Iterable[_Union[AlertMessage, _Mapping]]] = ...) -> None: ...

class SubscribeResponse(_message.Message):
    __slots__ = ("alert_status",)
    class AlertStatusMessage(_message.Message):
        __slots__ = ("subscribe_status", "type")
        class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            SUCCESS: _ClassVar[SubscribeResponse.AlertStatusMessage.Status]
            FAIL: _ClassVar[SubscribeResponse.AlertStatusMessage.Status]
        SUCCESS: SubscribeResponse.AlertStatusMessage.Status
        FAIL: SubscribeResponse.AlertStatusMessage.Status
        SUBSCRIBE_STATUS_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        subscribe_status: SubscribeResponse.AlertStatusMessage.Status
        type: AlertMessage
        def __init__(self, subscribe_status: _Optional[_Union[SubscribeResponse.AlertStatusMessage.Status, str]] = ..., type: _Optional[_Union[AlertMessage, _Mapping]] = ...) -> None: ...
    ALERT_STATUS_FIELD_NUMBER: _ClassVar[int]
    alert_status: _containers.RepeatedCompositeFieldContainer[SubscribeResponse.AlertStatusMessage]
    def __init__(self, alert_status: _Optional[_Iterable[_Union[SubscribeResponse.AlertStatusMessage, _Mapping]]] = ...) -> None: ...

class AlertSupportRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AlertSupportResponse(_message.Message):
    __slots__ = ("supported_alerts", "version_number")
    SUPPORTED_ALERTS_FIELD_NUMBER: _ClassVar[int]
    VERSION_NUMBER_FIELD_NUMBER: _ClassVar[int]
    supported_alerts: _containers.RepeatedScalarFieldContainer[AlertNotification.AlertType]
    version_number: int
    def __init__(self, supported_alerts: _Optional[_Iterable[_Union[AlertNotification.AlertType, str]]] = ..., version_number: _Optional[int] = ...) -> None: ...

class AlertMessage(_message.Message):
    __slots__ = ("type", "interval")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    type: AlertNotification.AlertType
    interval: int
    def __init__(self, type: _Optional[_Union[AlertNotification.AlertType, str]] = ..., interval: _Optional[int] = ...) -> None: ...

class AlertNotification(_message.Message):
    __slots__ = ("type", "AlertNotification")
    class AlertType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ACTIVITY_START: _ClassVar[AlertNotification.AlertType]
        ACTIVITY_STOP: _ClassVar[AlertNotification.AlertType]
        LAUNCH_MONITOR: _ClassVar[AlertNotification.AlertType]
    ACTIVITY_START: AlertNotification.AlertType
    ACTIVITY_STOP: AlertNotification.AlertType
    LAUNCH_MONITOR: AlertNotification.AlertType
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ALERTNOTIFICATION_FIELD_NUMBER: _ClassVar[int]
    type: AlertNotification.AlertType
    AlertNotification: AlertDetails
    def __init__(self, type: _Optional[_Union[AlertNotification.AlertType, str]] = ..., AlertNotification: _Optional[_Union[AlertDetails, _Mapping]] = ...) -> None: ...

class AlertDetails(_message.Message):
    __slots__ = ("state", "metrics", "error", "tilt_calibration")
    STATE_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    TILT_CALIBRATION_FIELD_NUMBER: _ClassVar[int]
    state: State
    metrics: Metrics
    error: Error
    tilt_calibration: CalibrationStatus
    def __init__(self, state: _Optional[_Union[State, _Mapping]] = ..., metrics: _Optional[_Union[Metrics, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ..., tilt_calibration: _Optional[_Union[CalibrationStatus, _Mapping]] = ...) -> None: ...

class State(_message.Message):
    __slots__ = ("state",)
    class StateType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STANDBY: _ClassVar[State.StateType]
        INTERFERENCE_TEST: _ClassVar[State.StateType]
        WAITING: _ClassVar[State.StateType]
        RECORDING: _ClassVar[State.StateType]
        PROCESSING: _ClassVar[State.StateType]
        ERROR: _ClassVar[State.StateType]
    STANDBY: State.StateType
    INTERFERENCE_TEST: State.StateType
    WAITING: State.StateType
    RECORDING: State.StateType
    PROCESSING: State.StateType
    ERROR: State.StateType
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: State.StateType
    def __init__(self, state: _Optional[_Union[State.StateType, str]] = ...) -> None: ...

class CalibrationStatus(_message.Message):
    __slots__ = ("status", "result")
    class StatusType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[CalibrationStatus.StatusType]
        IN_BOUNDS: _ClassVar[CalibrationStatus.StatusType]
        RECALIBRATION_SUGGESTED: _ClassVar[CalibrationStatus.StatusType]
        RECALIBRATION_REQUIRED: _ClassVar[CalibrationStatus.StatusType]
    UNKNOWN: CalibrationStatus.StatusType
    IN_BOUNDS: CalibrationStatus.StatusType
    RECALIBRATION_SUGGESTED: CalibrationStatus.StatusType
    RECALIBRATION_REQUIRED: CalibrationStatus.StatusType
    class CalibrationResult(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUCCESS: _ClassVar[CalibrationStatus.CalibrationResult]
        ERROR: _ClassVar[CalibrationStatus.CalibrationResult]
        UNIT_MOVING: _ClassVar[CalibrationStatus.CalibrationResult]
    SUCCESS: CalibrationStatus.CalibrationResult
    ERROR: CalibrationStatus.CalibrationResult
    UNIT_MOVING: CalibrationStatus.CalibrationResult
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    status: CalibrationStatus.StatusType
    result: CalibrationStatus.CalibrationResult
    def __init__(self, status: _Optional[_Union[CalibrationStatus.StatusType, str]] = ..., result: _Optional[_Union[CalibrationStatus.CalibrationResult, str]] = ...) -> None: ...

class Error(_message.Message):
    __slots__ = ("code", "severity", "deviceTilt")
    class ErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[Error.ErrorCode]
        OVERHEATING: _ClassVar[Error.ErrorCode]
        RADAR_SATURATION: _ClassVar[Error.ErrorCode]
        PLATFORM_TILTED: _ClassVar[Error.ErrorCode]
    UNKNOWN: Error.ErrorCode
    OVERHEATING: Error.ErrorCode
    RADAR_SATURATION: Error.ErrorCode
    PLATFORM_TILTED: Error.ErrorCode
    class Severity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        WARNING: _ClassVar[Error.Severity]
        SERIOUS: _ClassVar[Error.Severity]
        FATAL: _ClassVar[Error.Severity]
    WARNING: Error.Severity
    SERIOUS: Error.Severity
    FATAL: Error.Severity
    CODE_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    DEVICETILT_FIELD_NUMBER: _ClassVar[int]
    code: Error.ErrorCode
    severity: Error.Severity
    deviceTilt: Tilt
    def __init__(self, code: _Optional[_Union[Error.ErrorCode, str]] = ..., severity: _Optional[_Union[Error.Severity, str]] = ..., deviceTilt: _Optional[_Union[Tilt, _Mapping]] = ...) -> None: ...

class Tilt(_message.Message):
    __slots__ = ("roll", "pitch")
    ROLL_FIELD_NUMBER: _ClassVar[int]
    PITCH_FIELD_NUMBER: _ClassVar[int]
    roll: float
    pitch: float
    def __init__(self, roll: _Optional[float] = ..., pitch: _Optional[float] = ...) -> None: ...

class Metrics(_message.Message):
    __slots__ = ("shot_id", "shot_type", "ball_metrics", "club_metrics", "swing_metrics")
    class ShotType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PRACTICE: _ClassVar[Metrics.ShotType]
        NORMAL: _ClassVar[Metrics.ShotType]
    PRACTICE: Metrics.ShotType
    NORMAL: Metrics.ShotType
    SHOT_ID_FIELD_NUMBER: _ClassVar[int]
    SHOT_TYPE_FIELD_NUMBER: _ClassVar[int]
    BALL_METRICS_FIELD_NUMBER: _ClassVar[int]
    CLUB_METRICS_FIELD_NUMBER: _ClassVar[int]
    SWING_METRICS_FIELD_NUMBER: _ClassVar[int]
    shot_id: int
    shot_type: Metrics.ShotType
    ball_metrics: BallMetrics
    club_metrics: ClubMetrics
    swing_metrics: SwingMetrics
    def __init__(self, shot_id: _Optional[int] = ..., shot_type: _Optional[_Union[Metrics.ShotType, str]] = ..., ball_metrics: _Optional[_Union[BallMetrics, _Mapping]] = ..., club_metrics: _Optional[_Union[ClubMetrics, _Mapping]] = ..., swing_metrics: _Optional[_Union[SwingMetrics, _Mapping]] = ...) -> None: ...

class BallMetrics(_message.Message):
    __slots__ = ("launch_angle", "launch_direction", "ball_speed", "spin_axis", "total_spin", "spin_calculation_type", "golf_ball_type")
    class SpinCalculationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        RATIO: _ClassVar[BallMetrics.SpinCalculationType]
        BALL_FLIGHT: _ClassVar[BallMetrics.SpinCalculationType]
        OTHER: _ClassVar[BallMetrics.SpinCalculationType]
        MEASURED: _ClassVar[BallMetrics.SpinCalculationType]
    RATIO: BallMetrics.SpinCalculationType
    BALL_FLIGHT: BallMetrics.SpinCalculationType
    OTHER: BallMetrics.SpinCalculationType
    MEASURED: BallMetrics.SpinCalculationType
    class GolfBallType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[BallMetrics.GolfBallType]
        CONVENTIONAL: _ClassVar[BallMetrics.GolfBallType]
        MARKED: _ClassVar[BallMetrics.GolfBallType]
    UNKNOWN: BallMetrics.GolfBallType
    CONVENTIONAL: BallMetrics.GolfBallType
    MARKED: BallMetrics.GolfBallType
    LAUNCH_ANGLE_FIELD_NUMBER: _ClassVar[int]
    LAUNCH_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    BALL_SPEED_FIELD_NUMBER: _ClassVar[int]
    SPIN_AXIS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SPIN_FIELD_NUMBER: _ClassVar[int]
    SPIN_CALCULATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    GOLF_BALL_TYPE_FIELD_NUMBER: _ClassVar[int]
    launch_angle: float
    launch_direction: float
    ball_speed: float
    spin_axis: float
    total_spin: float
    spin_calculation_type: BallMetrics.SpinCalculationType
    golf_ball_type: BallMetrics.GolfBallType
    def __init__(self, launch_angle: _Optional[float] = ..., launch_direction: _Optional[float] = ..., ball_speed: _Optional[float] = ..., spin_axis: _Optional[float] = ..., total_spin: _Optional[float] = ..., spin_calculation_type: _Optional[_Union[BallMetrics.SpinCalculationType, str]] = ..., golf_ball_type: _Optional[_Union[BallMetrics.GolfBallType, str]] = ...) -> None: ...

class ClubMetrics(_message.Message):
    __slots__ = ("club_head_speed", "club_angle_face", "club_angle_path", "attack_angle")
    CLUB_HEAD_SPEED_FIELD_NUMBER: _ClassVar[int]
    CLUB_ANGLE_FACE_FIELD_NUMBER: _ClassVar[int]
    CLUB_ANGLE_PATH_FIELD_NUMBER: _ClassVar[int]
    ATTACK_ANGLE_FIELD_NUMBER: _ClassVar[int]
    club_head_speed: float
    club_angle_face: float
    club_angle_path: float
    attack_angle: float
    def __init__(self, club_head_speed: _Optional[float] = ..., club_angle_face: _Optional[float] = ..., club_angle_path: _Optional[float] = ..., attack_angle: _Optional[float] = ...) -> None: ...

class SwingMetrics(_message.Message):
    __slots__ = ("back_swing_start_time", "down_swing_start_time", "impact_time", "follow_through_end_time", "end_recording_time")
    BACK_SWING_START_TIME_FIELD_NUMBER: _ClassVar[int]
    DOWN_SWING_START_TIME_FIELD_NUMBER: _ClassVar[int]
    IMPACT_TIME_FIELD_NUMBER: _ClassVar[int]
    FOLLOW_THROUGH_END_TIME_FIELD_NUMBER: _ClassVar[int]
    END_RECORDING_TIME_FIELD_NUMBER: _ClassVar[int]
    back_swing_start_time: int
    down_swing_start_time: int
    impact_time: int
    follow_through_end_time: int
    end_recording_time: int
    def __init__(self, back_swing_start_time: _Optional[int] = ..., down_swing_start_time: _Optional[int] = ..., impact_time: _Optional[int] = ..., follow_through_end_time: _Optional[int] = ..., end_recording_time: _Optional[int] = ...) -> None: ...
