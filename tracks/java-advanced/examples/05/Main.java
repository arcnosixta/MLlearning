import java.nio.file.*;
import java.nio.charset.StandardCharsets;
public class Main {
    public static void main(String[] args) throws Exception {
        Path file=Files.createTempFile("imlearning-", ".txt");
        try {
            Files.writeString(file,"A\nB\n",StandardCharsets.UTF_8);
            try(var lines=Files.lines(file,StandardCharsets.UTF_8)) { System.out.println(lines.count()); }
        } finally { Files.deleteIfExists(file); }
    }
}
