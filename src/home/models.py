from django.db import models

class Level(models.Model):
    level_type = models.CharField(max_length=10, unique=True)
    added_now = models.DateTimeField(auto_now_add=True)
    update_now = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.level_type}"    

class Host(models.Model):
    host_name = models.CharField(max_length=255, unique=True)
    added_now = models.DateTimeField(auto_now_add=True)
    update_now = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.host_name}" 

class RequestMethod(models.Model):
    request_method_type = models.CharField(max_length=10, unique=True)
    added_now = models.DateTimeField(auto_now_add=True)
    update_now = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.request_method_type}"  
    
class LogEntry(models.Model):
    timestamp = models.CharField(max_length=30)
    date_time = models.DateTimeField()
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="log_entries_demo")  # ForeignKey to Level
    request_method = models.ForeignKey(RequestMethod, on_delete=models.CASCADE, related_name="log_entries_demo")  # ForeignKey to RequestMethod
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name="log_entries_demo")  # ForeignKey to Host
    log_string = models.TextField()
    added_now = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} - {self.level} - {self.host}"