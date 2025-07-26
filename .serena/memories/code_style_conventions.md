# Code Style and Conventions

## Python Style
- **Type hints**: Used throughout (e.g., `def function(param: str) -> bool`)
- **Docstrings**: Triple-quoted docstrings with Args/Returns sections
- **Variable naming**: Snake_case for variables and functions
- **Class naming**: PascalCase for classes (e.g., `MediaUtils`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `CHUNK_SIZE`, `LANGUAGE_VOICE_MAP`)

## Documentation Style
```python
def example_function(input_path: str, options: dict = None) -> bool:
    """
    Brief description of function purpose.
    
    Args:
        input_path: Path to input file
        options: Optional configuration dictionary
        
    Returns:
        bool: True if successful, False otherwise
    """
```

## Logging Patterns
- **Structured logging**: Uses loguru with context binding
- **Context loggers**: `logger.bind(key=value, ...)`
- **Log levels**: debug, info, error with appropriate context
- **Operation tracking**: Execution time, progress tracking

## Error Handling
- **Try-catch blocks**: Comprehensive exception handling
- **Validation**: Input validation with meaningful error messages
- **Return patterns**: Boolean returns for success/failure operations
- **Context preservation**: Error context maintained in logs

## FastAPI Patterns
- **Router organization**: Separate routers for different domains
- **Async/await**: Consistent async patterns
- **Request/response models**: Type-safe API contracts
- **Middleware**: Authentication and request processing
- **Dependency injection**: FastAPI dependency patterns

## File Organization
- **Module imports**: Standard library, third-party, local imports
- **Class methods**: Public methods, private methods, static methods
- **Code grouping**: Related functionality grouped together
- **Constants**: Defined at module level

## Naming Conventions
- **Files**: Snake_case (e.g., `v1_media_router.py`)
- **Variables**: Snake_case (e.g., `video_path`, `audio_length`)
- **Functions**: Snake_case (e.g., `merge_videos`, `get_video_info`)
- **Classes**: PascalCase (e.g., `MediaUtils`, `TTSManager`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `CHUNK_SIZE = 1024`)