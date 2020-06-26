# Flask Rate Limiter
Middleware for ip / api based rate limiting for flask web services.

# Usage

```python
from middleware import Middleware
from ratelimitsetup import RateLimitSetup

# Sqlite Setup
RateLimitSetup() 

# Hook ratelimit middleware
app.wsgi_app = Middleware(app.wsgi_app)
```

# Configuration
Configure the rate and the reset duration in ``.env``
```
# Default Rate
DEFAULT_RATE=15
# Rate reset duration in seconds
DEFAULT_DURATION=30
```

With this configuration a user is able to make 15 requests every 30 seconds


## License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/ssubedir/flask-rate-limiter/blob/master/LICENSE) file for details