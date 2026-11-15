SUBROUTINE TYPE_NanofluidGH(TIME, XIN, OUT, T, DT, SIM, PAR, INFO)
  USE TrnsysConstants
  USE TrnsysFunctions
  IMPLICIT NONE

  INTEGER :: INFO(15)
  DOUBLE PRECISION :: TIME, TIMESTEP, DT, SIM
  DOUBLE PRECISION :: XIN(4), OUT(4), PAR(14), T(2)

  DOUBLE PRECISION :: T_out, I_solar, Wind, T_fluid_inlet
  DOUBLE PRECISION :: T_in, T_roof
  DOUBLE PRECISION :: dT_in_dt, dT_roof_dt
  DOUBLE PRECISION :: h_out, Q_solar_roof, Q_solar_trans
  DOUBLE PRECISION :: Q_conv_in, Q_conv_out, Q_wall, Q_soil, Q_vent, Q_fluid

  IF (INFO(7) .EQ. -1) THEN
     T(1) = 15.0  
     T(2) = 15.0  
     RETURN
  ENDIF

  IF (INFO(7) .EQ. 1) THEN
     ! Inputs
     T_out         = XIN(1)
     I_solar       = XIN(2)
     Wind          = XIN(3)
     T_fluid_inlet = XIN(4)
     
     ! Parameters
     h_out        = PAR(1) + 2.0 * Wind 
     Q_solar_roof = (I_solar * PAR(2)) * PAR(6) 
     Q_solar_trans= (I_solar * PAR(2)) * PAR(5) 
     
     T_in   = T(1)
     T_roof = T(2)
     
     ! Heat Balances
     Q_conv_in  = PAR(13) * PAR(2) * (T_roof - T_in)
     Q_conv_out = h_out * PAR(2) * (T_roof - T_out)
     Q_wall     = PAR(11) * PAR(9) * (T_in - T_out) 
     Q_soil     = PAR(12) * PAR(2) * (T_in - 15.0)   
     Q_vent     = 1.2 * 1005.0 * PAR(10) * (T_in - T_out) 
     Q_fluid    = PAR(7) * PAR(8) * (T_roof - T_fluid_inlet) 
     
     ! Derivatives
     dT_in_dt   = (Q_solar_trans + Q_conv_in - Q_wall - Q_soil - Q_vent) / PAR(3)
     dT_roof_dt = (Q_solar_roof - Q_conv_in - Q_conv_out - Q_fluid) / PAR(4)
     
     T(1) = dT_in_dt
     T(2) = dT_roof_dt
     
     ! Outputs
     OUT(1) = T_in
     OUT(2) = T_roof
     OUT(3) = Q_fluid      
     OUT(4) = Q_solar_trans
  ENDIF
END SUBROUTINE