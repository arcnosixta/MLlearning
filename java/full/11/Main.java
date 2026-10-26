import java.time.*;
import java.time.format.*;
public class Main {
    public static void main(String[] args) {
        Clock clock = Clock.fixed(Instant.parse("2024-02-28T12:00:00Z"), ZoneOffset.UTC);
        LocalDate today = LocalDate.now(clock);
        var formatter = DateTimeFormatter.ofPattern("uuuu-MM-dd").withResolverStyle(ResolverStyle.STRICT);
        System.out.println(today.plusDays(1));
        System.out.println(LocalDate.parse("2024-02-29", formatter).isLeapYear());
        System.out.println(Duration.ofMinutes(90).toSeconds());
    }
}
