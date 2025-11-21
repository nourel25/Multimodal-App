from enum import Enum

class ResponseSignal(Enum):
    VIDEO_UPLOAD_SUCCESS = "video_upload_success"
    VIDEO_UPLOAD_FAILED = "video_upload_failed"
    PROCESSING_SUCCESS = "processing_success"
    PROCESSING_FAILED = "processing_failed"
    VIDEO_SIZE_EXCEEDED = "video_size_exceeded"
    VIDEO_VALIDATED_SUCCESS = "video_validate_successfully"
    AUDIO_TRANSCRIPT_SUCCESS = "audio_transcript_success"
    AUDIO_TRANSCRIPT_FAILED = "audio_transcript_failed"
    NO_URLS_FOUND_FOR_USER = "no_urls_found_for_user"
    USER_NOT_FOUND = "user_not_found"
    INSERT_INTO_VECTORDB_ERROR = "insert_into_vectordb_error"
    INSERT_INTO_VECTORDB_SUCCESS = "insert_into_vectordb_success"
    
    
