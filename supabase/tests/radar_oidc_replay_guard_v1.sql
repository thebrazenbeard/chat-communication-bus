begin;

do $$
declare
  test_jti text := '__radar_oidc_replay_test__' || substr(md5(clock_timestamp()::text || random()::text), 1, 12);
  first_result text;
  second_result text;
begin
  delete from radar.github_oidc_replay_guard where jti = test_jti;

  first_result := radar.consume_github_oidc_jti_v1(
    test_jti,
    clock_timestamp() + interval '10 minutes'
  );
  if first_result <> 'CONSUMED' then
    raise exception 'EXPECTED_CONSUMED_GOT_% for jti=%', first_result, test_jti;
  end if;

  second_result := radar.consume_github_oidc_jti_v1(
    test_jti,
    clock_timestamp() + interval '10 minutes'
  );
  if second_result <> 'REPLAY' then
    raise exception 'EXPECTED_REPLAY_GOT_% for jti=%', second_result, test_jti;
  end if;

  if (select count(*) from radar.github_oidc_replay_guard where jti = test_jti) <> 1 then
    raise exception 'OIDC_JTI_GUARD_NOT_UNIQUE for jti=%', test_jti;
  end if;

  raise notice 'Radar OIDC replay guard smoke test passed for %', test_jti;
end
$$;

rollback;
