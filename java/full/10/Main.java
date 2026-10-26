import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.regex.Pattern;
public class Main {
    public static void main(String[] args) {
        var matcher = Pattern.compile("([A-Z]{3})-([0-9]{3})").matcher("CSC-101");
        if (matcher.matches()) System.out.println(matcher.group(1) + ":" + matcher.group(2));
        String encoded = Base64.getEncoder().encodeToString("Java".getBytes(StandardCharsets.UTF_8));
        System.out.println(encoded);
        System.out.println(new String(Base64.getDecoder().decode(encoded), StandardCharsets.UTF_8));
    }
}
