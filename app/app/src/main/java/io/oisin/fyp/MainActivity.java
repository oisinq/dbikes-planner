package io.oisin.fyp;

import android.os.Bundle;
import android.util.Log;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import io.oisin.fyp.model.Direction;

public class MainActivity extends AppCompatActivity {
    ArrayList<Direction> directions = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.recycle_main);

        RequestQueue queue = Volley.newRequestQueue(this);

        queue.add(new StringRequest(Request.Method.GET,
                "https://oisin-flask-test.herokuapp.com/?start=53.330667,-6.258590&end=53.348778,-6.240998",
                new Response.Listener<String>() {
            @Override
            public void onResponse(String response) {
                try {
                    JSONArray route = new JSONObject(response).getJSONObject("fastest_cycle_route").getJSONArray("marker");

                    for (int i = 1; i < route.length(); i++) {
                        JSONObject directionObj = route.getJSONObject(i).getJSONObject("@attributes");

                        String streetName = directionObj.getString("name");
                        String turn = "";

                        if (directionObj.getString("turn").isEmpty()) {
                            turn = "Straight on";
                        } else {
                            turn = directionObj.getString("turn");
                        }

                        double distance = directionObj.getDouble("distance");
                        double time = directionObj.getDouble("time");

                        directions.add(new Direction(turn, distance, time, streetName));
                    }

                    DirectionsAdapter adapter = new DirectionsAdapter(directions);

                    // Lookup the recyclerview in activity layout
                    RecyclerView recyclerView = findViewById(R.id.recyclerView);

                    recyclerView.setAdapter(adapter);
                    recyclerView.setLayoutManager(new LinearLayoutManager(getApplicationContext()));
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
        }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                Log.e("RouteActivity", "error with route request");
            }
        }));
    }

}
