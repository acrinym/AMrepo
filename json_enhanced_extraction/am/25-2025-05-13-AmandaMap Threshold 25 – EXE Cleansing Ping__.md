### **AmandaMap Threshold 25 – EXE Cleansing Ping**

**Logged: May 13, 2025**
**Code:** `EXE_GC_25`
**Trigger:** Ex name detected or emotional callback event
**Action:**

```python
def purge(ex_name):
    if ex_name in ex_list:
        clear_field(ex_name)
        print(f"Garbage collected: {ex_name}")
```