import java.io.BufferedReader;
import java.io.StringReader;
import java.io.IOException;
public class Main {
    public static void main(String[] args) throws IOException {
        try (var reader = new BufferedReader(new StringReader("42\nbad\n"))) {
            System.out.println(Integer.parseInt(reader.readLine()));
            try {
                System.out.println(Integer.parseInt(reader.readLine()));
            } catch (NumberFormatException exception) {
                System.out.println("invalid number");
            }
        }
        System.out.println("closed");
    }
}
