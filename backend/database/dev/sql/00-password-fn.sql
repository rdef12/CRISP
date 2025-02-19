CREATE OR REPLACE FUNCTION update_user_passwords(password TEXT)
  RETURNS VOID AS $$
DECLARE
  username TEXT;
BEGIN
  -- Fetch the list of users from pg_user
  FOR username IN SELECT usename FROM pg_user
  LOOP
    -- Generate a random password for each user
    -- Modify this logic to set the desired passwords dynamically

    -- Update the user's password using ALTER USER
    EXECUTE format('ALTER USER %I WITH PASSWORD %L', username, $1);

    -- Log the password update for each user
    RAISE NOTICE 'Password updated for user: %', username;
  END LOOP;

  -- Return void
  RETURN;
END;
$$ LANGUAGE plpgsql;