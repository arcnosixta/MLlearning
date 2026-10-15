import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.io.IOException;
public class Main {
    public static void main(String[] args) throws IOException {
        Path file = Files.createTempFile("imlearning-", ".txt");
        try {
            Files.writeString(file, "Aida:80\n", StandardCharsets.UTF_8);
            System.out.print(Files.readString(file, StandardCharsets.UTF_8));
        } finally { Files.deleteIfExists(file); }
    }
}
