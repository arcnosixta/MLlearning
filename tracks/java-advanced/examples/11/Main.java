import java.net.URI;import java.net.http.*;import java.time.Duration;
public class Main {public static void main(String[] args){var request=HttpRequest.newBuilder(URI.create("https://example.invalid/tasks")).timeout(Duration.ofSeconds(2)).GET().build();System.out.println(request.method());System.out.println(request.timeout().orElseThrow().toSeconds());}}
