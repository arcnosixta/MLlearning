import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.io.IOException;
public class Main {
    public static void main(String[] args) throws IOException {
        Path directory = Files.createTempDirectory("java-course-");
        Path file = directory.resolve("notes.txt");
        try {
            Files.writeString(file, "Java\nSQL\n", StandardCharsets.UTF_8);
            try (var lines = Files.lines(file, StandardCharsets.UTF_8)) {
                System.out.println(lines.count());
            }
            ByteBuffer buffer = ByteBuffer.allocate(8);
            buffer.putInt(42).putInt(7).flip();
            System.out.println(buffer.getInt() + buffer.getInt());
        } finally {
            Files.deleteIfExists(file);
            Files.deleteIfExists(directory);
        }
    }
}
