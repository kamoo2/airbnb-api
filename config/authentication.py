import jwt
from django.conf import settings
from users.models import User
from rest_framework import authentication
from rest_framework import exceptions


class JWTAuthentication(authentication.BaseAuthentication):
    # 기본적으로 장고는 settings에 설정한 모든 Authentication방법을 다시도함
    # 만약 다 시도해봤는데 Authentication이 안된다. ? 그러면 credentials not provided 에러발생

    # Custom Authentication 사용시 주의할점
    # Custom Authentication은 실패했을시에 반드시 None을 return 해줘야함
    def authenticate(self, request):

        try:
            # token이 None이라는 것은 header로 JWT TOKEN이 전달되지 않았다는 것이고 이는 인증실패를 뜻함
            # 우리는 headers로 받는 모든 정보는 META에서 찾을수 있다.
            token = request.META.get("HTTP_AUTHORIZATION")
            if token is None:
                return None

            # unpacking 기법 Header로 JWT blablatoken.... 을 전달했다.
            # split(" ") -> 띄워쓰기가 있으면 그둘을 나눠서 각 변수에 매핑해줌
            # 따라서 아래 코드같은 경우에는 jwt 에는 JWT가 들어가고 jwt_token에는 진짜 토큰이 들어감
            # header로 token을 받아올때는 관습적으로 앞에 JWT나 X-JWT 등등 붙여줌
            # 관습적으로 저런 이름을 붙이는거지 POTATO도 가능 하고 뭐든 가능함
            xjwt, jwt_token = token.split(" ")

            # token을 받아왔으니 이제는 decoded 해줄 차례
            decoded = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
            pk = decoded.get("pk")
            user = User.objects.get(pk=pk)
            # 우리는 client로부터 header에 token을 담아서 데이터를 받았고
            # 그 데이터를 decode해서 담긴 정보를 가져왔고
            # 그 정보에는 user의 pk가 담겨져 있기때문에 그 pk를 이용해
            # user object를 찾아서 return 해준다.
            # 단 return 할때 user만 리턴하면 에러발생 아래와 같이 None도 리턴해줘야함
            return (user, None)
        except (ValueError, User.DoesNotExist):
            return None
        except jwt.exceptions.DecodeError:
            raise exceptions.AuthenticationFailed(detail="JWT Format Invalid")
