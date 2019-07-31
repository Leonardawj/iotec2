<?php
	$servername = "localhost";
	$username = "root";
	$password = "password";
	$dbname = "iotgarbagemonitoring";

	// Create connection
	$conn = new mysqli($servername, $username, $password, $dbname);
	// Check connection
	if ($conn->connect_error) {
		die("Connection failed: " . $conn->connect_error);
	} 

	$sql = "SELECT *from sensor_data ORDER BY id DESC LIMIT 1";
	$result = $conn->query($sql);

	if ($result->num_rows == 1)
	{
		$row = $result->fetch_assoc();
		$sensor1 = $row["sensor1"];
		$sensor2 = $row["sensor2"];
	}
	else 
	{
		echo "0 results";
	}
	
	$conn->close();
?>

<!DOCTYPE html>
<html lang="en">
	<head>
		<title>IOT Garbage Monitoring system</title>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<meta http-equiv="refresh" content="5">
		<link rel="stylesheet" href="bootstrap.min.css">
		<script src="bootstrap.min.js"></script>
		<link rel="stylesheet" href="styles.css">
	</head>
	<body>
		<div class="jumbotron text-center">
		  <h1>IOT Garbage Monitoring system</h1>
		</div>
		<div class="container">
			<table class="table">
				<tr>
					<th class="jumbotron text-center">Container1</th>
					<th class="jumbotron text-center">Container2</th>
				</tr>
				<tr>
					<th>
						<div class="center">
							<div class="progress progress-bar-vertical">
								<div class="progress-bar" role="progressbar" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100" <?php echo "style=\"height: ".$sensor1."%;\""; ?> > </div>
							</div>
						</div> 
						<div> <?php echo "Sensor1 : ". $sensor1; ?> </div>
					</th>
					<th>
						<div class="center">
							<div class="progress progress-bar-vertical">
								<div class="progress-bar" role="progressbar" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100" <?php echo "style=\"height: ".$sensor2."%;\""; ?> > </div>  
							</div>
						</div>
						<div> <?php echo "Sensor2 : ". $sensor2; ?> </div>
					</th>
				</tr>
			</table>
			<br> <br> <br>
			<div class="jumbotron text-center">
				<h1>Data Log</h1>
			</div>
			<?php
				$conn = new mysqli($servername, $username, $password, $dbname);
				if ($conn->connect_error) {
					die("Connection failed: " . $conn->connect_error);
				} 
				$sql  = 'SELECT * FROM `sensor_data` WHERE 1';
				$result = $conn->query($sql);
				if ($result->num_rows > 0) 
				{
					echo "<table class=\"table\">"; 
					//echo "<tr><td>NO of Data : " . $result->num_rows . "</td></tr>";
					echo "<tr><td>ID</td><td>Sensor1</td><td>Sensor2</td><td>Date Time</td></tr>";
								
					while($row = $result->fetch_array(MYSQLI_ASSOC))
					{
						echo "<tr><td>" . $row['id'] . "</td><td>" . $row['sensor1'] . "</td><td>" . $row['sensor2'] . "</td><td>" . $row['date'] . "</td></tr>";
					}
					echo "</table>";
					$result->close();
				}
			?>
		</div>
	</body>
</html>
