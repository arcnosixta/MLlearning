import java.sql.*;
import javax.sql.rowset.*;
public class Main {
    static void report(ResultSet rows) throws SQLException {
        int count = 0, sum = 0;
        while (rows.next()) { count++; sum += rows.getInt("grade"); }
        System.out.println("students=" + count);
        System.out.println("average=" + (count == 0 ? "none" : Integer.toString(sum / count)));
    }
    static void database(String url) throws SQLException {
        try (Connection connection = DriverManager.getConnection(url, "sa", "")) {
            try (Statement schema = connection.createStatement()) {
                schema.executeUpdate("CREATE TABLE course_students(id INT PRIMARY KEY, grade INT NOT NULL)");
            }
            connection.setAutoCommit(false);
            try (PreparedStatement insert = connection.prepareStatement("INSERT INTO course_students(id,grade) VALUES (?,?)")) {
                for (int i = 1; i <= 2; i++) {
                    insert.setInt(1, i);
                    insert.setInt(2, i == 1 ? 85 : 95);
                    insert.addBatch();
                }
                insert.executeBatch();
                connection.commit();
            } catch (SQLException original) {
                try { connection.rollback(); } catch (SQLException rollback) { original.addSuppressed(rollback); }
                throw original;
            }
            connection.setAutoCommit(true);
            try (PreparedStatement query = connection.prepareStatement("SELECT grade FROM course_students ORDER BY id");
                 ResultSet rows = query.executeQuery()) { report(rows); }
        }
    }
    public static void main(String[] args) throws SQLException {
        if (args.length > 0) { database(args[0]); return; }
        try (CachedRowSet rows = RowSetProvider.newFactory().createCachedRowSet()) {
            RowSetMetaDataImpl metadata = new RowSetMetaDataImpl();
            metadata.setColumnCount(1);
            metadata.setColumnName(1, "grade");
            metadata.setColumnType(1, Types.INTEGER);
            rows.setMetaData(metadata);
            for (int grade : new int[]{85, 95}) {
                rows.moveToInsertRow(); rows.updateInt(1, grade); rows.insertRow(); rows.moveToCurrentRow();
            }
            rows.beforeFirst();
            report(rows);
        }
    }
}
