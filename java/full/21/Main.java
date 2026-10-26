import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.concurrent.*;
public class Main {
    public static void main(String[] args) throws Exception {
        InetAddress loopback = InetAddress.getLoopbackAddress();
        try (ServerSocket server = new ServerSocket(0, 1, loopback)) {
            server.setSoTimeout(3000);
            FutureTask<String> echo = new FutureTask<>(() -> {
                try (Socket socket = server.accept()) {
                    socket.setSoTimeout(3000);
                    var reader = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
                    var writer = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8));
                    String line = reader.readLine();
                    writer.write(line.toUpperCase(Locale.ROOT) + "\n");
                    writer.flush();
                    return "done";
                }
            });
            Thread worker = new Thread(echo);
            worker.start();
            try (Socket socket = new Socket()) {
                socket.connect(new InetSocketAddress(loopback, server.getLocalPort()), 3000);
                socket.setSoTimeout(3000);
                socket.getOutputStream().write("hello\n".getBytes(StandardCharsets.UTF_8));
                socket.getOutputStream().flush();
                var reader = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
                System.out.println(reader.readLine());
            }
            echo.get(4, TimeUnit.SECONDS);
            worker.join();
        }
        URI uri = URI.create("https://example.org/course?lang=ru");
        System.out.println(uri.getScheme());
        System.out.println(uri.getPath());
    }
}
