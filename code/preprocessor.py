import re
import pandas as pd

def preprocess(data):
    print(f"DEBUG: Raw data length: {len(data)}")
    print(f"DEBUG: First 500 chars of data: {data[:500]}")
    
    patterns = [
        r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s',  # DD/MM/YYYY, HH:MM - 
        r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s',     # DD/MM/YYYY, HH:MM 
        r'\d{1,2}-\d{1,2}-\d{2,4},\s\d{1,2}:\d{2}\s-\s',  # DD-MM-YYYY, HH:MM - 
        r'\d{1,2}\.\d{1,2}\.\d{2,4},\s\d{1,2}:\d{2}\s-\s', # DD.MM.YYYY, HH:MM - 
        r'\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\]', 
    ]
    
    pattern = None
    messages = []
    dates = []
    `   M,+HGAQ`
    for p in patterns:
        print(f"DEBUG: Trying pattern: {p}")
        test_messages = re.split(p, data)[1:]
        test_dates = re.findall(p, data)
        print(f"DEBUG: Found {len(test_messages)} messages and {len(test_dates)} dates with pattern {p}")
        
        if len(test_messages) > 0 and len(test_dates) > 0:
            pattern = p
            messages = test_messages
            dates = test_dates
            print(f"DEBUG: Using pattern: {pattern}")
            break
    
    if not pattern or len(messages) == 0:
        print("DEBUG: No valid pattern found, trying alternative parsing...")
        # Fallback: try to split by lines and look for date patterns
        lines = data.split('\n')
        messages = []
        dates = []
        current_message = ""
        
        for line in lines:
            if re.match(r'\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}', line):
                if current_message:
                    messages.append(current_message.strip())
                current_message = line
            else:
                current_message += "\n" + line
        
        if current_message:
            messages.append(current_message.strip())
        
        # Extract dates from messages
        for msg in messages:
            date_match = re.search(r'\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}', msg)
            if date_match:
                dates.append(date_match.group())
            else:
                dates.append("")
    
    print(f"DEBUG: Final - Found {len(messages)} messages and {len(dates)} dates")

    if len(messages) != len(dates):
        print(f"DEBUG: Mismatch in messages ({len(messages)}) and dates ({len(dates)}) count")
        min_len = min(len(messages), len(dates))
        messages = messages[:min_len]
        dates = dates[:min_len]

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    print(f"DEBUG: DataFrame shape after initial creation: {df.shape}")
    print(f"DEBUG: First few user_messages: {df['user_message'].head().tolist()}")
    
    # Convert message_date type with error handling
    try:
        if pattern == patterns[0]:  # DD/MM/YYYY, HH:MM - 
            df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %H:%M - ')
        elif pattern == patterns[1]:  # DD/MM/YYYY, HH:MM 
            df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %H:%M ')
        elif pattern == patterns[2]:  # DD-MM-YYYY, HH:MM - 
            df['message_date'] = pd.to_datetime(df['message_date'], format='%d-%m-%Y, %H:%M - ')
        elif pattern == patterns[3]:  # DD.MM.YYYY, HH:MM - 
            df['message_date'] = pd.to_datetime(df['message_date'], format='%d.%m.%Y, %H:%M - ')
        elif pattern == patterns[4]:  # [DD/MM/YYYY, HH:MM:SS]
            df['message_date'] = pd.to_datetime(df['message_date'], format='[%d/%m/%Y, %H:%M:%S]')
        else:
            # Try to parse with pandas' automatic date detection
            df['message_date'] = pd.to_datetime(df['message_date'], errors='coerce')
    except Exception as e:
        print(f"DEBUG: Date parsing error: {e}")
        # Fallback: try automatic parsing
        df['message_date'] = pd.to_datetime(df['message_date'], errors='coerce')

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []
    for i, message in enumerate(df['user_message']):
        if i < 3:  # Debug first 3 messages
            print(f"DEBUG: Message {i}: '{message[:100]}...'")
        
        # Try different patterns to extract user and message
        user_message = None
        
        # Pattern 1: Name: message (most common)
        match1 = re.match(r'^([^:]+):\s(.+)$', message, re.DOTALL)
        if match1:
            user_message = (match1.group(1).strip(), match1.group(2).strip())
        
        # Pattern 2: [Date] Name: message
        if not user_message:
            match2 = re.match(r'^\[.*?\]\s*([^:]+):\s(.+)$', message, re.DOTALL)
            if match2:
                user_message = (match2.group(1).strip(), match2.group(2).strip())
        
        # Pattern 3: Date - Name: message
        if not user_message:
            match3 = re.match(r'^.*?-\s*([^:]+):\s(.+)$', message, re.DOTALL)
            if match3:
                user_message = (match3.group(1).strip(), match3.group(2).strip())
        
        # Pattern 4: Just look for any colon
        if not user_message:
            colon_pos = message.find(':')
            if colon_pos > 0:
                potential_user = message[:colon_pos].strip()
                potential_message = message[colon_pos+1:].strip()
                # Check if potential_user looks like a name (not too long, no special chars)
                if len(potential_user) < 50 and not re.search(r'[^\w\s\-\.]', potential_user):
                    user_message = (potential_user, potential_message)
        
        if user_message:
            users.append(user_message[0])
            messages.append(user_message[1])
            if i < 3:
                print(f"DEBUG: Extracted user: '{user_message[0]}', message: '{user_message[1][:50]}...'")
        else:
            # Check if it's a system message
            if any(keyword in message.lower() for keyword in ['added', 'removed', 'left', 'joined', 'created', 'changed']):
                users.append('group_notification')
                messages.append(message.strip())
            else:
                # If no pattern matches, treat as group notification
                users.append('group_notification')
                messages.append(message.strip())
            if i < 3:
                print(f"DEBUG: No pattern matched, treating as group notification")

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)
    
    print(f"DEBUG: Final DataFrame shape: {df.shape}")
    print(f"DEBUG: Unique users: {df['user'].unique()}")
    print(f"DEBUG: Sample messages: {df['message'].head().tolist()}")
    
    # Remove rows with empty messages
    df = df[df['message'].str.strip() != '']
    print(f"DEBUG: After removing empty messages: {df.shape}")

    # Handle date processing with error handling
    try:
        df['only_date'] = df['date'].dt.date
        df['year'] = df['date'].dt.year
        df['month_num'] = df['date'].dt.month
        df['month'] = df['date'].dt.month_name()
        df['day'] = df['date'].dt.day
        df['day_name'] = df['date'].dt.day_name()
        df['hour'] = df['date'].dt.hour
        df['minute'] = df['date'].dt.minute

        period = []
        for hour in df['hour']:
            if pd.isna(hour):
                period.append("Unknown")
            elif hour == 23:
                period.append(str(int(hour)) + "-" + str('00'))
            elif hour == 0:
                period.append(str('00') + "-" + str(int(hour + 1)))
            else:
                period.append(str(int(hour)) + "-" + str(int(hour + 1)))

        df['period'] = period
    except Exception as e:
        print(f"DEBUG: Date processing error: {e}")
        # Create default values if date processing fails
        df['only_date'] = pd.Timestamp.now().date()
        df['year'] = 2024
        df['month_num'] = 1
        df['month'] = 'January'
        df['day'] = 1
        df['day_name'] = 'Monday'
        df['hour'] = 12
        df['minute'] = 0
        df['period'] = '12-13'

    print(f"DEBUG: Final processed DataFrame shape: {df.shape}")
    print(f"DEBUG: Date range: {df['date'].min()} to {df['date'].max()}")
    
    return df