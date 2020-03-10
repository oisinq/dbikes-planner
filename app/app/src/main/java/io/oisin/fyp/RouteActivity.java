package io.oisin.fyp;

import android.content.Intent;
import android.location.Location;
import android.os.Bundle;
import android.util.Log;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.Dot;
import com.google.android.gms.maps.model.Gap;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.MarkerOptions;
import com.google.android.gms.maps.model.PatternItem;
import com.google.android.gms.maps.model.PolylineOptions;
import com.google.android.libraries.places.api.model.Place;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.Arrays;
import java.util.List;

import androidx.appcompat.app.AppCompatActivity;

public class RouteActivity extends AppCompatActivity implements OnMapReadyCallback {

    private GoogleMap mMap;
    private Place place;

    @Override
    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_route);


        // Obtain the SupportMapFragment and get notified when the map is ready to be used.
        SupportMapFragment mapFragment = (SupportMapFragment) getSupportFragmentManager()
                .findFragmentById(R.id.map);
        mapFragment.getMapAsync(this);

        Intent intent = getIntent();
        place = intent.getParcelableExtra("place");

        Location location = intent.getParcelableExtra("start");

        // Instantiate the RequestQueue.
        RequestQueue queue = Volley.newRequestQueue(this);

     //   String start = + location.getLatitude() + "," + location.getLongitude();
        String start = "53.330667,-6.258590";

        String end = place.getLatLng().latitude + "," + place.getLatLng().longitude;

        String url = "https://oisin-flask-test.herokuapp.com/?start="+ start + "&end="+end;

        // Request a string response from the provided URL.
        StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        // Display the first 500 characters of the response string.
                        try {
                            JSONObject map = new JSONObject(response);

                            JSONObject cycleRoute = map.getJSONObject("cycle_route");
                            JSONObject startWalkingRoute = map.getJSONObject("start_walking_route");
                            JSONObject endWalkingRoute = map.getJSONObject("end_walking_route");

                            mMap.addPolyline(getCycleLine(cycleRoute));
                            mMap.addPolyline(getWalkingRoute(startWalkingRoute));
                            mMap.addPolyline(getWalkingRoute(endWalkingRoute));

                            Log.d("RouteActivity", "onResponse: " + response);
                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                Log.e("RouteActivity", "error with route request");
            }
        });

        queue.add(stringRequest);

    }

    private PolylineOptions getCycleLine(JSONObject cycleRoute) throws JSONException {
        String[] coordinates = cycleRoute.getJSONArray("marker").getJSONObject(0)
                .getJSONObject("@attributes").getString("coordinates").split(" ");
        PolylineOptions line = new PolylineOptions();

        for (String coordinate : coordinates) {
            String[] lnglat = coordinate.split(",");

            // List<PatternItem> pattern = Arrays.asList(new Dot(), new Gap(20), new Dash(30), new Gap(20));
            line.add(new LatLng(Double.parseDouble(lnglat[1]), Double.parseDouble(lnglat[0])));
        }

        return line;
    }

    private PolylineOptions getWalkingRoute(JSONObject walkingRoute) throws JSONException {
        JSONArray coordinates = walkingRoute.getJSONArray("features").getJSONObject(0)
                .getJSONObject("geometry").getJSONArray("coordinates");

        PolylineOptions line = new PolylineOptions();

        for (int i = 0; i < coordinates.length(); i++) {
            JSONArray array = coordinates.getJSONArray(i);

            String longitude = array.getString(0);
            String latitude = array.getString(1);

            line.add(new LatLng(Double.parseDouble(latitude), Double.parseDouble(longitude)));
        }

        List<PatternItem> pattern = Arrays.asList(new Dot(), new Gap(10));

        return line.pattern(pattern);
    }


    /**
     * Manipulates the map once available.
     * This callback is triggered when the map is ready to be used.
     * This is where we can add markers or lines, add listeners or move the camera. In this case,
     * we just add a marker near Sydney, Australia.
     * If Google Play services is not installed on the device, the user will be prompted to install
     * it inside the SupportMapFragment. This method will only be triggered once the user has
     * installed Google Play services and returned to the app.
     */
    @Override
    public void onMapReady(GoogleMap googleMap) {
        mMap = googleMap;

        // Add a marker in Sydney and move the camera
        mMap.addMarker(new MarkerOptions().position(place.getLatLng()).title(place.getName()).snippet(place.getAddress()));
        mMap.moveCamera(CameraUpdateFactory.zoomTo(16f));
        mMap.moveCamera(CameraUpdateFactory.newLatLng(place.getLatLng()));
    }
}
